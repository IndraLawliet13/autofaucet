# FLOW

## Primary request flow

The public template starts with a plain `requests.Session` and tries to keep the faster non-browser path alive as long as possible.

Core steps:

1. load local env configuration
2. seed the session with the configured auth cookie name/value
3. request the target faucet page
4. parse cooldown state, form state, and token state
5. call the configured solver endpoint for a Turnstile token
6. submit the claim POST request

## Browser-assisted fallback

When the page returns blocked states such as `403` or `503`, the template can call `CloudflareBypasser`.

That helper does several things:

- opens a SeleniumBase browser session
- syncs cookies from the requests session into the browser
- injects JavaScript to intercept Turnstile render parameters
- optionally asks a custom solver for a token using those captured parameters
- calls the original browser callback with the solved token
- syncs cookies and user-agent details back into the requests session

## Debug behavior

The template intentionally keeps local debug capture behavior when something is wrong:

- `error_403.html`
- `error_logout.html`
- `error_no_form.html`
- `cf_fail_debug.html`

These files are ignored from git because they can contain live session/page details.

## Recommended interpretation

This repo is best treated as a troubleshooting-oriented automation template, not a polished end-user application. The main public value is the hybrid request-plus-browser pattern for dealing with Cloudflare/Turnstile protected flows.
