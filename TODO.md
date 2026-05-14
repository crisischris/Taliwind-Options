# TODO

Priority scale: 0 = highest, 5 = lowest

---

## Bugs & Investigations

- `[0]` Investigate why we're getting exactly 60 short and long puts — looks like an artificial cap
- `[1]` A ticker shouldn't require all 3 sections (short, long, moonshot) — surface tickers with only one qualifying category

## Frontend

- `[1]` implement calls page logic
- `[2]` Confirm Mobile-friendly layout

## Scanner & Options Engine

- `[3]` Evaluate whether running N times per day makes sense (pre-market, open, close)

## Infrastructure

- `[0]` Add beta and gamma stages
- `[1]` Investigate yfinance / API usage limits — assess exhaustion risk at current and projected call volume
- `[4]` Plan for scale: CDN, database, storage strategy as user base grows and persitent URL.

## Testing

- `[0]` Add integration tests for the scanner logic in beta / gamma
- `[0]` Add unit tests

## Product & Features

- `[3]` User profiles and saved settings
- `[3]` Define and scope premium feature set
- `[4]` Add beta / gamma staging environments
- `[4]` Evaluate what a full webapp architecture looks like (auth, persistence, etc.)

## Growth

- `[5]` Publicize — determine distribution strategy

## Premium Product & Features

- dynamic filters (client side changes?  API (have to consider this from a scalabilty mindset if so)?)
- `[2]` Report retros — track how many flagged plays were actually ITM at expiry; surface most-profitable plays and optimal hold duration
- longer lookbacks (is this something we care about?)
