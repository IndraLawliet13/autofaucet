import os
import time
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

from cf_bypasser import CloudflareBypasser

init(autoreset=True)

# ================= KONFIGURASI LOKAL =================
BASE_URL = os.getenv("AUTOFAUCET_BASE_URL", "https://autofaucet.org").rstrip("/")
TARGET_URL = os.getenv("AUTOFAUCET_TARGET_URL", f"{BASE_URL}/earn/faucet")
SITE_KEY = os.getenv("AUTOFAUCET_SITE_KEY", "0x4AAAAAAAeegevyhnJu7zGA").strip()
POST_URL = os.getenv("AUTOFAUCET_POST_URL", "").strip()
API_KEY = os.getenv("AUTOFAUCET_2CAPTCHA_API_KEY", "").strip()
COOKIE_NAME = os.getenv("AUTOFAUCET_COOKIE_NAME", "").strip()
COOKIE_VALUE = os.getenv("AUTOFAUCET_COOKIE_VALUE", "").strip()
EXPECTED_USERNAME = os.getenv("AUTOFAUCET_EXPECTED_USERNAME", "").strip()
DIRECT_SOLVER_API_URL = os.getenv(
    "AUTOFAUCET_DIRECT_SOLVER_API_URL",
    "https://api.nekolabs.web.id/tools/bypass/cf-turnstile",
).strip()
HEADLESS = os.getenv("AUTOFAUCET_HEADLESS", "0").lower() in {"1", "true", "yes"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin": BASE_URL,
    "Referer": TARGET_URL,
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}


class TurnstileSolver:
    def __init__(self, api_key=None):
        self.api_url = DIRECT_SOLVER_API_URL
        self.api_key = api_key

    def solve(self, domain_url: str, site_key: str) -> str:
        payload = {"url": domain_url, "siteKey": site_key}
        print(f"{Fore.YELLOW}[Captcha] {Style.RESET_ALL}Minta token ke API...", end="\r")
        try:
            resp = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60,
                verify=False,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success") == 1:
                    print(f"{Fore.GREEN}[Captcha] {Style.RESET_ALL}Token diterima!             ")
                    return data.get("result")
        except Exception as e:
            print(f"{Fore.RED}[Captcha] Error: {e}")
        return None

    def solve_custom(self, captured_params: dict) -> str:
        if not self.api_key:
            print(f"{Fore.RED}[Captcha] 2Captcha API key belum diisi.")
            return None

        print(f"{Fore.YELLOW}[Captcha] {Style.RESET_ALL}Mengambil parameter dari browser...")
        params = {
            "target_url": captured_params.get("pageurl"),
            "site_key": captured_params.get("sitekey"),
            "user_agent": captured_params.get("userAgent"),
            "action": captured_params.get("action"),
            "data": captured_params.get("data"),
            "pagedata": captured_params.get("pagedata"),
        }

        data0 = {
            "key": self.api_key,
            "method": "turnstile",
            "sitekey": params["site_key"],
            "action": params["action"],
            "data": params["data"],
            "pagedata": params["pagedata"],
            "useragent": params["user_agent"],
            "json": 1,
            "pageurl": params["target_url"],
            "proxytype": "http",
        }

        print(f"{Fore.YELLOW}[Captcha] {Style.RESET_ALL}Minta token ke 2Captcha...", end="\r")
        try:
            resp = requests.post("https://2captcha.com/in.php", data=data0, verify=False, timeout=60)
            req_id = resp.json()["request"]
            while True:
                solu = requests.get(
                    f"https://2captcha.com/res.php?key={self.api_key}&action=get&json=1&id={req_id}",
                    timeout=60,
                ).json()
                if solu["request"] == "CAPCHA_NOT_READY":
                    time.sleep(8)
                elif "ERROR" in solu["request"]:
                    print(solu["request"])
                    return None
                else:
                    break
        except Exception as e:
            print(f"{Fore.RED}[Captcha] Error: {e}")
            return None

        print(f"{Fore.GREEN}[Captcha] {Style.RESET_ALL}Token diterima!             ")
        return solu["request"]


def save_debug_html(content, filename="vps_debug.html"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"{Fore.MAGENTA}[DEBUG] HTML disimpan ke: {filename}")
    except Exception as e:
        print(f"[DEBUG] Gagal simpan HTML: {e}")


def validate_env():
    missing = []
    if not POST_URL:
        missing.append("AUTOFAUCET_POST_URL")
    if not COOKIE_NAME or not COOKIE_VALUE:
        missing.append("AUTOFAUCET_COOKIE_NAME/AUTOFAUCET_COOKIE_VALUE")
    if not SITE_KEY:
        missing.append("AUTOFAUCET_SITE_KEY")
    if missing:
        raise RuntimeError("Missing required local config: " + ", ".join(missing))


def main():
    validate_env()
    print(f"{Fore.CYAN}[*] Memulai bot AutoFaucet (template publik)...")

    session = requests.Session()
    session.headers.update(HEADERS)
    requests.utils.add_dict_to_cookiejar(session.cookies, {COOKIE_NAME: COOKIE_VALUE})

    solver = TurnstileSolver(api_key=API_KEY)
    bypasser = CloudflareBypasser(headless=HEADLESS, solver_instance=solver)

    while True:
        try:
            print(f"\n{Fore.BLUE}[>] Mengambil halaman faucet...")
            resp = session.get(TARGET_URL, timeout=30, verify=False)

            if resp.status_code in [403, 503]:
                print(f"{Fore.RED}    (!) Terblokir {resp.status_code}. Menyimpan HTML...")
                session = requests.Session()
                session.headers.update(HEADERS)
                requests.utils.add_dict_to_cookiejar(session.cookies, {COOKIE_NAME: COOKIE_VALUE})
                save_debug_html(resp.text, "error_403.html")

                print(f"{Fore.YELLOW}    (i) Membuka browser bypass...")
                session = bypasser.solve(session, TARGET_URL)
                continue

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")

                if EXPECTED_USERNAME and EXPECTED_USERNAME not in resp.text and "Sign In" in resp.text:
                    print(f"{Fore.RED}[!] Logout. Menyimpan HTML untuk analisis...")
                    save_debug_html(resp.text, "error_logout.html")
                    break

                timer_container = soup.find(id="faCliHolder")
                if timer_container and timer_container.has_attr("data-next"):
                    next_claim_time = int(timer_container["data-next"])
                    current_time = int(time.time())
                    if next_claim_time > current_time:
                        wait_seconds = next_claim_time - current_time + 5
                        print(f"{Fore.YELLOW}(i) Timer aktif. Menunggu {wait_seconds} detik.")
                        while wait_seconds > 0:
                            print(f"    Menunggu... {wait_seconds}s ", end="\r")
                            time.sleep(1)
                            wait_seconds -= 1
                        continue

                claim_form = soup.find("form", id="faCliForm")
                if not claim_form:
                    print(f"{Fore.RED}(!) Form tidak ditemukan.")
                    save_debug_html(resp.text, "error_no_form.html")
                    time.sleep(10)
                    continue

                c_token_input = claim_form.find("input", {"name": "c-token"})
                if not c_token_input:
                    print(f"{Fore.RED}[!] Token c-token hilang.")
                    time.sleep(5)
                    continue

                c_token = c_token_input.get("value")
                print(f"{Fore.GREEN}[Data] Token form: {Fore.YELLOW}{c_token[:15]}...")

                token = solver.solve(TARGET_URL, SITE_KEY)
                if token:
                    payload = {
                        "au-data": "",
                        "c-type": "3",
                        "c-token": c_token,
                        "cf-turnstile-response": token,
                    }

                    print(f"{Fore.MAGENTA}[Exec] Menembak claim...")
                    post_resp = session.post(POST_URL, data=payload, timeout=30, verify=False)

                    try:
                        json_res = post_resp.json()
                        if json_res.get("success"):
                            print(f"{Fore.GREEN}✅ CLAIM SUKSES! Reward: {json_res.get('newReward')}")
                        else:
                            print(f"{Fore.RED}(X) Gagal: {json_res.get('message')}")
                    except Exception:
                        print(f"{Fore.RED}(!) Error parsing JSON response.")

                print(f"{Fore.CYAN}(Zzz) Refreshing dalam 5 detik...")
                time.sleep(5)

        except Exception as e:
            print(f"{Fore.RED}Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
