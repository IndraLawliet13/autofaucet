# autofaucet

![Python](https://img.shields.io/badge/Python-Automation-3776AB?logo=python&logoColor=white)
![Browser](https://img.shields.io/badge/Browser-SeleniumBase-43B02A)
![Focus](https://img.shields.io/badge/Focus-Cloudflare%20%2B%20Turnstile-111827)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

Python automation template for the AutoFaucet claim flow, including Turnstile solving, Cloudflare bypass assistance via SeleniumBase, and local debug capture for blocked sessions.

This public candidate is prepared as a safe showcase version of a private debug-oriented working setup. Live cookies, claim endpoints, API keys, and local debug artifacts are intentionally removed or converted into environment variables.

## Highlights

- requests-based claim loop template
- browser-assisted Cloudflare fallback path
- direct solver and 2Captcha-assisted modes
- explicit local env model for sensitive runtime data
- debug HTML capture when blocked or malformed states appear

## Included files

- `template_bot.py` - sanitized claim-flow template
- `cf_bypasser.py` - SeleniumBase helper for Cloudflare/Turnstile interception and browser-session sync
- `test_sb.py` - tiny SeleniumBase smoke test
- `requirements.txt`
- `.env.example`
- `LICENSE`

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
set -a
source .env
set +a
python3 template_bot.py
```

## Required local variables

- `AUTOFAUCET_POST_URL`
- `AUTOFAUCET_COOKIE_NAME`
- `AUTOFAUCET_COOKIE_VALUE`
- `AUTOFAUCET_SITE_KEY`

Optional:
- `AUTOFAUCET_2CAPTCHA_API_KEY`
- `AUTOFAUCET_EXPECTED_USERNAME`
- `AUTOFAUCET_DIRECT_SOLVER_API_URL`
- `AUTOFAUCET_HEADLESS`

## Runtime shape

The public template preserves this general flow:

1. prepare a requests session with browser-like headers
2. hydrate local login cookie state
3. fetch the faucet page
4. detect cooldown / ready / blocked states
5. solve Turnstile directly or via browser-assisted fallback
6. submit the claim payload to the configured POST endpoint
7. save debug HTML locally when blocked or malformed states appear

## Documentation

- `docs/FLOW.md`

## Security notes

- Never commit `.env`.
- Never commit live cookies, API keys, or POST endpoints captured from a session.
- Treat debug HTML dumps as sensitive because they can include live page/session details.

## Disclaimer

Shared for educational and automation-architecture reference. Use it responsibly and according to the target platform's rules and your own risk tolerance.
