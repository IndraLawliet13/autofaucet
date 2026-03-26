# AutoFaucet Quickstart

## Requirements

- Python 3.10+
- A local `.env` created from `.env.example`
- Optional browser support if you want to use the SeleniumBase fallback path

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
set -a
source .env
set +a
```

## Run the sanitized template

```bash
python3 template_bot.py
```

## Optional browser smoke test

```bash
python3 test_sb.py
```

## Public-safe note

The public repo intentionally omits live cookies, claim endpoints, API keys, and local debug artifacts captured from real sessions.
