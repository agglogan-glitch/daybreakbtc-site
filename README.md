# daybreakbtc.com — static site

Two pages, no JavaScript, no trackers, no cookies, no web fonts or CDNs. Everything the pages load
is in this folder.

| File | URL |
| --- | --- |
| `index.html` | `https://daybreakbtc.com/` — landing page |
| `privacy/index.html` | `https://daybreakbtc.com/privacy` (and `/privacy/`) — works on any static host, no rewrites |
| `404.html` | shown for unknown paths (GitHub Pages, Netlify and Porkbun use this name) |
| `styles.css` | shared styles; colors from the app theme (`src/theme/tokens.ts`) |
| `logo.svg`, `favicon.ico`, `favicon.png`, `apple-touch-icon.png` | the ₿ mark from the app's Welcome screen (orange circle). The app's `assets/icon.png` and `assets/favicon.png` are still the Expo template icons, so they were **not** copied. |
| `CNAME` | `daybreakbtc.com` (used by GitHub Pages; harmless elsewhere) |
| `build_privacy.py` | regenerates `privacy/index.html` from `docs/privacy-policy.md` |

## Editing the policy

1. Edit `docs/privacy-policy.md` (the source of truth).
2. Run `python3 site/build_privacy.py` from the repo root (Python 3 standard library only).
3. Commit both files.

## ⚠️ Before publishing

- **The policy is a draft, not legal advice. Have a lawyer review it before publishing.**
- Fill in `[EFFECTIVE DATE]` (suggest the public launch date) and `[CONTACT EMAIL]` in `docs/privacy-policy.md`, then rebuild.
- After the lawyer review, remove the orange "Draft" note: delete the `> **Draft…**` quote at the top of
  `docs/privacy-policy.md` (and the HTML comment above it), then rebuild. The public page should not keep a
  draft banner or footer.
- Re-check the facts if the app's network code changes (see "Audit notes" below).

## Deploying

The app repo is private and proprietary, so **don't publish this repo**. Copy only the contents of
`site/` to the host. See the hosting recommendation in the Dev Lead report (GitHub Pages from a small
separate public repo containing only these files, or Porkbun Static Hosting). After DNS is live, turn on HTTPS
(GitHub: Settings → Pages → Enforce HTTPS).

Quick local preview: `python3 -m http.server -d site 8000` and open http://localhost:8000/.

## Audit notes (app at commit 697c2dc)

Network endpoints the app calls (all plain HTTPS GETs, no keys, no cookies, no extra headers beyond `Accept: application/json`; `src/wallet/http.ts:18-23`):

- `blockstream.info/api` (primary) and `mempool.space/api` (fallback) — address balance and payment history; the public address is in the URL path. Only after the user taps "OK, show my balance" (`src/wallet/sync.ts:186-196`); then on adding an address or "Check for updates". `src/wallet/providers/esplora.ts:83-84`, `src/wallet/providers/index.ts:9`.
- `www.bitstamp.net/api/v2/ohlc/btcusd` then `mempool.space/api/v1/historical-price` — daily prices missing after the bundled series; automatic ~1.2 s after app start (`src/app/_layout.tsx:49`) and on the Price tab. `src/prices/sources.ts:57,93`, `src/prices/index.ts:35`.
- `api.coingecko.com/api/v3/simple/price` then `mempool.space/api/v1/prices` — live price (cached 10 min). `src/costBasis/priceService.ts:54,77`, `src/services.ts:59-73`.
- `api.coingecko.com/api/v3/coins/bitcoin/history?date=…` then `mempool.space/api/v1/historical-price?timestamp=…` — the price on a payment's date (date only, no address). `src/costBasis/priceService.ts:46,66`.
- Outbound links (open the browser, user-tapped): buy/wallet suggestions `src/util/region.ts:150-155` via `src/app/(tabs)/wallet.tsx:512`; lesson credits and licenses `src/app/lesson/[id].tsx:61-93`; price-data credits `src/app/(tabs)/price.tsx:579-583`, `src/app/(tabs)/settings.tsx:143-182`.

Not present: analytics, crash reporting, ads, `expo-updates` (no OTA update checks), WebSockets, remote images.
Fonts are bundled (`src/i18n/fonts.ts`); the `fonts.gstatic.com` strings in the web bundle are package metadata and were never requested in a live capture.
