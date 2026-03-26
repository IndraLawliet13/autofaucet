# autofaucet

[![CI](https://github.com/IndraLawliet13/autofaucet/actions/workflows/python-smoke.yml/badge.svg)](https://github.com/IndraLawliet13/autofaucet/actions/workflows/python-smoke.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Browser](https://img.shields.io/badge/Browser-SeleniumBase-43B02A)
![Focus](https://img.shields.io/badge/Focus-Cloudflare%20%2B%20Turnstile-111827)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

Python automation template for the AutoFaucet claim flow, including Turnstile solving, Cloudflare bypass assistance via SeleniumBase, and local debug capture for blocked sessions.

This public candidate is prepared as a safe showcase version of a private debug-oriented working setup. Live cookies, claim endpoints, API keys, and local debug artifacts are intentionally removed or converted into environment variables.

## Overview

`autofaucet` is a supporting-showcase repo focused on the reusable parts of a faucet claimant pipeline:

- a requests-based claim template
- a SeleniumBase helper for Cloudflare and Turnstile handling
- a tiny smoke test for browser setup validation

The public repo is intentionally structured as a template and reference, not a live runnable dump of one private account.

## Highlights

- requests-based claim loop template
- browser-assisted Cloudflare fallback path
- direct solver and 2Captcha-assisted modes
- explicit local env model for sensitive runtime data
- debug HTML capture when blocked or malformed states appear

## Tech stack

- Python 3.10+
- requests
- BeautifulSoup
- SeleniumBase
- colorama

## Project structure

- `template_bot.py` - sanitized claim-flow template
- `cf_bypasser.py` - SeleniumBase helper for Cloudflare and Turnstile interception
- `test_sb.py` - tiny SeleniumBase smoke test
- `docs/FLOW.md` - runtime flow notes
- `docs/QUICKSTART.md` - copy-pasteable local bootstrap steps
- `.env.example` - required local secret/config template

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
4. detect cooldown, ready, or blocked states
5. solve Turnstile directly or via browser-assisted fallback
6. submit the claim payload to the configured POST endpoint
7. save debug HTML locally when blocked or malformed states appear

## Documentation

- `docs/QUICKSTART.md`
- `docs/FLOW.md`

## Scope and limitations

- This repo is a public-safe template, not a packaged end-user faucet client.
- The actual target endpoint, cookie value, and any solver API keys must stay local.
- Browser automation behavior can vary based on Cloudflare changes and local driver setup.

## Security notes

- Never commit `.env`.
- Never commit live cookies, API keys, or POST endpoints captured from a session.
- Treat debug HTML dumps as sensitive because they can include live page and session details.

## Disclaimer

Shared for educational and automation-architecture reference. Use it responsibly and according to the target platform's rules and your own risk tolerance.
