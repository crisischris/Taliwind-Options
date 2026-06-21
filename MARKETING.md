# Tailwind Options: Marketing

## Core Blurb

I built a free tool that scans the S&P 500 and Nasdaq 100 twice a day looking for asymmetric options plays.

The idea behind it: when a stock goes up 500% in a year, the options market tends to price in more upside. That makes puts on those names surprisingly cheap relative to the actual downside risk. Same logic applies in reverse for momentum names on the call side.

Every market open and midday the scanner runs, filters for the biggest gainers, then combs through option chains looking for cheap OTM contracts with real open interest and a realistic shot at paying off. Results are sorted into short, long, and moonshot categories.

No login. No paywall. No email required.

tailwindoptions.com

---

## Launch Plan

**Pre-launch (today, May 20):** Write Product Hunt listing copy, gather screenshots, line up upvoters.

**Launch day: Tuesday May 21**

| Time (ET)       | Channel          | Notes |
|-----------------|------------------|-------|
| 12:01 AM PT     | Product Hunt     | Launch at midnight PT; have upvoters ready for the first hour |
| 7:00–8:00 AM PT | Hacker News      | Post early PT for max front page runway |
| 8:00–10:00 AM   | r/investing      | Pre-open or early session |
| 8:30–9:30 AM    | Twitter / X      | Pre-market finance crowd peaks here |
| 8:30–10:00 AM   | r/stocks         | Pre-open or early session |
| 9:00–11:00 AM   | IndieHackers     | Weekday morning |
| 9:30–10:30 AM   | r/options        | Right at market open |
| 9:30–11:00 AM   | r/thetagang      | Market hours |
| 10:00–11:00 AM  | r/wallstreetbets | Peak during market hours |

---

## Platform Notes

### Reddit
- Read each subreddit's rules before posting. Self-promotion tolerance varies by sub.
- Lead with "here's what I built and how it works", not "check out my site"
- Engage with every comment

### Hacker News
- Title format: "Show HN: I built a twice-daily scanner that finds cheap OTM options on extreme gainers"
- Technical story first: Lambda + EventBridge + S3 + CloudFront, no servers, runs on a schedule
- Options angle is secondary

### Twitter/X
- Hashtags: #options #fintwit
- Post the actual plays the scanner surfaces. Let the signals do the marketing.
- Keep it to 2-3 sentences max 

### Product Hunt
- Do not launch same day as HN
- Need: tagline, description, screenshots, a maker comment, 5+ people lined up to upvote at launch

---


---

## Platform-Specific Copy

---

### Product Hunt

**Tagline:**
> Twice-daily options scanner for asymmetric plays on extreme market gainers

**Description:**
```
Tailwind Options scans the S&P 500 and Nasdaq 100 every market open and
midday, finds stocks with extreme trailing gains, and surfaces cheap OTM
options contracts with real liquidity.

The idea: when a stock goes up 500%+ in a year, the options market tends to
underprice downside risk. Puts become surprisingly cheap relative to actual
tail risk. The scanner finds those setups automatically. No research required.

→ Puts scanner: finds cheap OTM puts on extreme S&P 500 / Nasdaq gainers
→ Calls scanner: finds cheap OTM calls on momentum names across thematic ETFs
→ Results sorted into short, long, and moonshot categories
→ Scores each contract by return multiple × prob ITM

No login. No email. No paywall. Free forever.
```

**Maker comment:**
```
Hey PH! Builder here.

I built this because every morning I was manually scanning options chains on
the biggest gainers looking for cheap asymmetric setups. After a few months
I automated the whole thing.

The tech: Python Lambda on EventBridge Scheduler, runs at 9:31 and 12:31 AM
ET, writes JSON to S3, static React frontend on CloudFront. No servers, no
database, costs about $2/month to run.

Would love any feedback on the scanner logic, the UX, or the methodology.
Happy to answer questions about the build or the options thesis.
```

**Post at:** Tuesday 12:01 AM PT. Have 5+ supporters ready to upvote within the first hour. Early velocity drives front-page placement.

---

### r/options

**Title:**
> I built a free scanner that finds cheap OTM puts on extreme S&P 500 / Nasdaq gainers. Runs twice daily, no login required.

**Body:**
```
The thesis: when a stock is up 500%+ over the last year, the options market
tends to misprice downside risk. Implied vol on the calls gets bid up, but
cheap OTM puts are often sitting there with real open interest and a realistic
shot at paying off if the name mean-reverts.

I built a scanner that runs every market open and midday to find these setups. It:
- Pulls 1-year price history for the full S&P 500 and Nasdaq 100
- Filters for names above a gain threshold
- Combs option chains for OTM puts with max IV, min open interest, and a
  DTE window
- Scores each contract by return multiple × prob ITM
- Sorts results into short (< 120 DTE), long (120–365 DTE), and moonshot (365+ DTE)

Same logic runs on the call side for momentum names held across thematic ETFs
(ARKK, SMH, AIQ, BOTZ, etc.).

Everything's free, no login, no email, no paywall. I'm not selling anything.

tailwindoptions.com

Happy to talk through the methodology or the edge cases. There are plenty.
```

**Post at:** Tuesday or Wednesday, 9:30–10:30 AM ET

---

### r/thetagang

**Title:**
> Built a scanner to surface cheap OTM options on extreme gainers. Good for seeing what the other side of your short premium looks like.

**Body:**
```
Mostly a theta crew here so this is a bit different from your usual positioning,
but I figured it'd be useful context:

I built a free tool that scans S&P 500 / Nasdaq names with extreme YTD gains and
surfaces cheap OTM puts and calls on them. The scanner filters on IV, open
interest, cost as a % of stock price, and DTE, then scores by return multiple
and prob ITM.

If you're short puts or calls on any of the high-flying names, this shows you
what the other side of your trade looks like from a debit perspective: how cheap
those contracts are, what open interest looks like, and how the market is pricing
tail risk.

No login, no email, completely free.

tailwindoptions.com

Curious whether anyone here has a view on tail risk mispricing on extreme
gainers. The vol skew situation on some of these names is pretty interesting.
```

**Post at:** Tuesday or Wednesday, 9:30–11:00 AM ET

---

### r/investing

**Title:**
> I built a free options scanner focused on asymmetric risk setups on extreme S&P 500 / Nasdaq gainers

**Body:**
```
I want to share a tool I built and be transparent about the methodology so you
can judge whether it's useful.

The idea: stocks that gain 500%+ in a year often see their put options become
underpriced relative to actual tail risk. The market bids up call IV on these
names, but OTM puts can be cheap even when the probability of a correction is
non-trivial.

The scanner runs twice daily (market open and midday) against the full S&P 500
and Nasdaq 100. It filters on:
- Minimum gain threshold over the trailing year
- Max ask as a % of stock price (keeps contracts affordable)
- Max IV (avoid overpaying for vol)
- Min open interest (liquidity filter)
- DTE range (30–730 days)

Results are scored by expected return multiple × probability ITM, then split
into short, long, and moonshot categories.

There's also a call scanner for momentum names held across thematic ETFs:
ARKK, ARKX, SMH, AIQ, BOTZ, and a few others.

No login required, completely free. I'm not selling anything. Built this
for my own use and figured others might find it useful.

tailwindoptions.com

Happy to discuss the methodology or the risks. Options on volatile names
carry real downside and this is not a trade recommendation tool.
```

**Post at:** Tuesday or Wednesday, 8:00–10:00 AM ET

---

### r/stocks

**Title:**
> Built a free scanner that surfaces cheap OTM options plays on the biggest S&P 500 / Nasdaq gainers. No login. Runs twice daily.

**Body:**
```
Quick share: I built a free tool for finding asymmetric options setups on
extreme gainers.

Simple logic: when a stock goes up 500%+ in a year, the market often
misprices downside risk. The scanner finds those names and surfaces cheap OTM
puts with real liquidity. Same logic reversed for calls on momentum names
across thematic ETFs.

It runs at market open and midday. No login, no email, no paywall.

tailwindoptions.com

If you've been watching any of the high-flying names and have a view on
whether they're due for a pullback, the scanner might be a useful addition
to your research. Even if you don't trade options, it's an interesting
lens on how the market is pricing tail risk on some of these names.
```

**Post at:** Tuesday or Wednesday, 8:30–10:00 AM ET

---

### r/wallstreetbets

**Title:**
> I built a robot that finds cheap lottery tickets on the most overextended stocks in the market. Free, runs twice a day.

**Body:**
```
The play: find stocks that went up 500%+ and buy cheap OTM puts before they
come back to earth.

I built a scanner that wakes up every morning and midday, digs through the
S&P 500 and Nasdaq, finds the most cooked names, and surfaces the cheapest
options contracts on them. Filters for real open interest, not garbage. Scores
by return multiple. Sorts into short-dated, long-dated, and moonshot plays.

Also does calls on momentum names across the meme ETFs (ARKK, SMH, etc.) for
the degens who want to ride the wave instead of bet against it.

Free. No login. No email. No "premium tier." Just the plays.

tailwindoptions.com

Not financial advice, I am not a financial advisor, I'm just a guy who built
a Lambda function.
```

**Post at:** Tuesday–Thursday, 10:00–11:00 AM ET

---

### Hacker News: Show HN

**Title:**
> Show HN: A free options scanner built on thematic investment theses

**Body:**
```
Most options scanners give you a firehose of contracts sorted by IV or volume
and let you filter. I built this one around themes.

The scanner runs against 7 investment theses — things like "extreme gainers
tend to have cheap OTM puts because the market anchors on recent upside" or
"stocks breaking to 52-week highs on volume enter price discovery." Each theme
has explicit entry rules, a defined universe, and a scoring model. You pick the
thesis you believe in and see the best-fit contracts for it.

Under the hood: EventBridge triggers a Lambda twice a day (market open +
midday), which scans the S&P 500 and Nasdaq 100 options chains, scores
contracts by return multiple × prob ITM, and writes JSON reports to S3. A
React/Vite static site on CloudFront reads the reports. No database, no
servers, essentially zero running cost.

Free, no login, no email required.

Would love feedback on the thesis framing, the scoring model, or the
architecture.

https://tailwindoptions.com
```

**Post at:** Tuesday, 7:00–8:00 AM PT (10:00–11:00 AM ET). Posting early PT gives the thread the longest runway before the afternoon traffic peak.

---

### Twitter / X

**Launch tweet:**
```
I built a free scanner that finds cheap OTM options on the most overextended
stocks in the S&P 500 and Nasdaq.

Runs every morning and midday. No login, no paywall.

[screenshot of day's best plays]

#options #fintwit
```
*(link in first reply)*

**Signal tweet (use on a day the scanner surfaces something compelling):**
```
Scanner just flagged [TICKER]. Up [X]% trailing year, $[price] puts at
$[ask] ask, [DTE] DTE. [return_multiple]x return if it hits the strike.

This is what asymmetric looks like.

tailwindoptions.com #options #fintwit
```

**Post at:** Tuesday or Wednesday, 8:30–9:30 AM ET

---

### IndieHackers

**Title:**
> I built a twice-daily options scanner with Lambda + S3. Here's what it took.

**Body:**
```
I've been lurking on IH for a while and wanted to share what I've been
building.

**What it does**

Tailwind Options scans the S&P 500 and Nasdaq 100 twice a day, finds stocks
with extreme trailing gains, and surfaces cheap OTM options contracts on those
names. The thesis: when a stock goes up 500%+ the market tends to misprice
downside risk. Puts get cheap. The scanner finds those setups automatically.

**The stack**

- EventBridge Scheduler triggers a Lambda at 9:31 and 12:31 AM ET
- Lambda pulls 1-year price history via yfinance, filters gainers, scans
  option chains, scores and writes JSON to S3
- CloudFront serves a static React site that reads those JSON reports
- CDK manages all infra. Full two-stage pipeline (beta → prod) on push to main.
- Total cost: ~$2/month

No database. No auth service. No servers. Just a Lambda, a scheduler, and
an S3 bucket.

**The journey**

This started as a personal spreadsheet. I kept manually checking the same
data every morning and finally decided to automate it. The hardest part wasn't
the options logic. Getting the data pipeline reliable enough to actually trust
took the most work. yfinance is free but unpredictable. Added retry logic,
caching, and a lot of defensive handling before I felt comfortable relying on it.

**Where it is now**

Live at tailwindoptions.com. Completely free, no login, no paywall. I'm
figuring out distribution now, which is why I'm posting here.

Happy to talk stack, options logic, or the build process.
```

**Post at:** Tuesday or Wednesday, 9:00–11:00 AM ET

---

## Results Log

| Date | Channel | Link | Upvotes / Engagement | Traffic spike |
|------|---------|------|----------------------|---------------|
| | | | | |
