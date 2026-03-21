import time
import sys
from seleniumbase import SB
from requests.cookies import create_cookie
from urllib.parse import urlparse

class CloudflareBypasser:
    def __init__(self, headless=False, solver_instance=None):
        self.headless = headless
        self.solver = solver_instance

    def _sync_to_browser(self, sb, session, url):
        try:
            parsed = urlparse(url)
            root_url = f"{parsed.scheme}://{parsed.netloc}"
            sb.open(root_url)
            
            for c in session.cookies:
                cookie_dict = {
                    "name": c.name,
                    "value": c.value,
                    "path": "/", 
                    "secure": False
                }
                try: sb.driver.add_cookie(cookie_dict)
                except: pass
            
            sb.driver.refresh()
            time.sleep(2)
        except Exception as e:
            print(f"   [Bypasser] Gagal sync ke browser: {e}")

    def _sync_to_session(self, sb, session):
        try:
            user_agent = sb.get_user_agent()
            session.headers.update({"User-Agent": user_agent})
            
            cookies = sb.driver.get_cookies()
            for c in cookies:
                c_obj = create_cookie(
                    name=c.get("name"),
                    value=c.get("value"),
                    domain=c.get("domain"),
                    path=c.get("path", "/"),
                    secure=c.get("secure", False),
                    rest={'HttpOnly': c.get("httpOnly", False)}
                )
                session.cookies.set_cookie(c_obj)
        except Exception as e:
            print(f"   [Bypasser] Gagal sync balik: {e}")

    def solve(self, session, url):
        print(f"\n   [Bypasser] 🛡️ Memulai bypass untuk: {url}")
        
        # --- DETEKSI LINGKUNGAN ---
        # Argumen ini adalah "Kunci Inggris" agar Chrome jalan di VPS Root
        extra_args = ""
        if sys.platform == "linux" or sys.platform == "linux2":
            extra_args = "--no-sandbox --disable-dev-shm-usage --disable-gpu --disable-setuid-sandbox --remote-debugging-port=9222"

        js_intercept = """
        console.clear = () => console.log('Console was cleared');
        window.cf_params = null;
        
        const i = setInterval(()=>{
            if (window.turnstile) {
                clearInterval(i);
                window.turnstile.render = (a,b) => {
                    let params = {
                        sitekey: b.sitekey,
                        pageurl: window.location.href,
                        data: b.cData,
                        pagedata: b.chlPageData,
                        action: b.action,
                        userAgent: navigator.userAgent,
                        json: 1
                    };
                    console.log('Intercepted!');
                    window.cf_params = params; // Simpan ke variabel global
                    window.cfCallback = b.callback; // Simpan fungsi callback asli
                    return;
                };
            }
        }, 50);
        """

        # Kita gunakan format string untuk 'chromium_arg'
        with SB(uc=True, test=True, headless=self.headless, chromium_arg=extra_args) as sb:
            try:
                self._sync_to_browser(sb, session, url)
                sb.open(url)
                
                sb.execute_script(js_intercept)
                print("   [Bypasser] Mendeteksi Turnstile...")

                time.sleep(1)
                sb.refresh()

                sb.execute_script(js_intercept)
                print("   [Bypasser] Menunggu parameter Turnstile terambil...")
                captured_params = None
                start_time = time.time()
                while time.time() - start_time < 30:
                    captured_params = sb.execute_script("return window.cf_params;")
                    if captured_params:
                        print("   [Bypasser] ✅ Parameter DITEMUKAN!")
                        break
                    
                    # Cek kalau sudah lolos duluan (kadang cookie lama masih sakti)
                    if "Just a moment" not in sb.get_title():
                        print("   [Bypasser] Lolos tanpa captcha!")
                        self._sync_to_session(sb, session)
                        return session
                        
                    time.sleep(1)

                if captured_params:
                    # 5. Oper data ke Solver (Nekolabs / 2Captcha / dll)
                    print(f"   [Bypasser] Sitekey: {captured_params.get('sitekey')}")
                    print(f"   [Bypasser] Action: {captured_params.get('action')}")
                    print(f"   [Bypasser] PageURL: {captured_params.get('pageurl')}")
                    
                    # Panggil Solver Custom User
                    if self.solver:
                        token = self.solver.solve_custom(captured_params)
                        
                        if token:
                            print("   [Bypasser] Token diterima, menyuntikkan callback...")
                            # 6. Panggil fungsi callback asli di browser dengan token hasil solve
                            sb.execute_script(f"cfCallback('{token}');")
                            time.sleep(5) # Beri waktu Cloudflare memproses token
                        else:
                            print("   [Bypasser] Gagal mendapatkan token dari API.")
                    else:
                        print("   [Bypasser] Solver tidak dikonfigurasi di class Bypasser.")

                # 7. Tunggu hasil akhir (Lolos atau Tidak)
                if "Just a moment" not in sb.get_title():
                    print("   [Bypasser] ✅ Bypass Berhasil!")
                    self._sync_to_session(sb, session)
                else:
                    print("   [Bypasser] ❌ Masih nyangkut di Cloudflare.")
                    # Debug source
                    with open("cf_fail_debug.html", "w", encoding="utf-8") as f:
                        f.write(sb.get_page_source())

            except Exception as e:
                print(f"   [Bypasser] ❌ Error: {e}")

        return session