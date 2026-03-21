from seleniumbase import SB

with SB(uc=True, headless=True) as sb:
    sb.open("https://www.google.com")
    print("TITLE:", sb.get_title())

