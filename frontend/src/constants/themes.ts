export interface JudgementCall {
  rule:   string
  detail: string
}

export interface ThemeDefinition {
  id:       string
  name:     string
  shortName: string
  tagline:  string
  thesis:   string
  icon:     string
  page:     'puts' | 'calls'
  judgementCalls?: {
    intro: string
    rules: JudgementCall[]
  }
}

const JC_INTRO = 'These are the rules baked into the scanner. Each one is a deliberate choice, not a given:'

const JC_OTM_PUTS:   JudgementCall = { rule: 'Out-of-the-money puts only',  detail: 'We want downside optionality, not intrinsic value. ITM puts are excluded.' }
const JC_OTM_CALLS:  JudgementCall = { rule: 'Out-of-the-money calls only', detail: 'We want continuation optionality, not intrinsic value. ITM calls are excluded.' }
const JC_LIQUIDITY:  JudgementCall = { rule: 'Minimum liquidity',           detail: 'Open interest ≥ 10, or any volume traded today, or a recorded last price.' }
const JC_SCORING:    JudgementCall = { rule: 'Scored by expected value × prob ITM × liquidity', detail: 'Options are ranked by risk-neutral expected payoff (Black-Scholes, integrated across the full payoff distribution — not just strike ÷ ask) divided by ask, multiplied by probability of expiring in-the-money and a 0–1 liquidity factor that penalizes wide spreads and thin open interest on a gradient. This balances raw upside against realistic odds and how tradeable the contract actually is.' }
const JC_TOP_10:     JudgementCall = { rule: 'Top 10 per bucket',           detail: 'Short-dated (< 6 months) and long-dated / LEAPs (6+ months) are capped at 10 each, sorted by score. Moonshots — the top 5 by raw return multiple — are surfaced separately.' }

export const THEMES: ThemeDefinition[] = [
  // ── Puts themes ──────────────────────────────────────────────────────────
  {
    id:        'mean-reversion',
    name:      'Mean Reversion (default)',
    shortName: 'Mean Rev.',
    tagline:   'Cheap OTM puts on extreme gainers',
    thesis:
      'Stocks with 500%+ trailing 12-month gains tend to mean-revert. The move may be fundamental, but the options market regularly underprices downside risk on extreme gainers. This scanner finds those names and surfaces cheap out-of-the-money puts on them. The setup is asymmetric — small premium at risk, large payoff if the correction plays out.',
    icon: '📉',
    page: 'puts',
    judgementCalls: {
      intro: JC_INTRO,
      rules: [
        { rule: 'Universe',                   detail: 'S&P 500 and NASDAQ 100 constituents only — liquid, well-known names where options markets are active.' },
        { rule: '500%+ over 1 year',          detail: 'The stock must have appreciated at least 500% over the trailing 12 months. Below that threshold the mean-reversion thesis is weaker.' },
        JC_OTM_PUTS,
        { rule: 'Expiry between 60 and 1,000 DTE', detail: 'Too short and there is no time for the thesis to play out. Too long and pricing becomes speculative. The sweet spot is roughly 2 months to 3 years out.' },
        { rule: 'Ask ≤ 5% of stock price',    detail: 'Keeps the cost-of-insurance sensible. A put that costs more than 5% of the underlying is already pricing in meaningful downside.' },
        { rule: 'Implied volatility ≤ 200%',  detail: 'Extremely high IV means the market is already pricing in a crash. We want names where the put is still relatively cheap.' },
        JC_LIQUIDITY,
        JC_SCORING,
        JC_TOP_10,
      ],
    },
  },
  {
    id:        'broken-momentum',
    name:      'Broken Momentum',
    shortName: 'Breakdown',
    tagline:   'Cheap puts on former leaders now breaking down',
    thesis:
      'Stocks that made 52-week highs in the past six months but are now trading 20%+ below their peak — with volume rising on down days and shrinking on up days — are showing the classic distribution pattern. Smart money is exiting. This scanner identifies these broken leaders and surfaces cheap OTM puts. The setup has price confirmation: the thesis has already started playing out.',
    icon: '🔻',
    page: 'puts',

    judgementCalls: {
      intro: JC_INTRO,
      rules: [
        { rule: 'Universe',                   detail: 'S&P 500 and NASDAQ 100 constituents only — liquid names with active options markets.' },
        { rule: 'Made a 52-week high in the past 180 days', detail: 'The stock must have set a 52-week high within the last 6 months, confirming it was recently a market leader.' },
        { rule: '20%+ below peak',            detail: 'Currently trading at least 20% below the trailing 52-week high. Meaningful deterioration, not a routine dip.' },
        { rule: 'Distribution volume pattern', detail: 'Average down-day volume over the past 20 sessions must exceed average up-day volume — the hallmark of quiet institutional selling.' },
        JC_OTM_PUTS,
        { rule: 'Expiry between 60 and 365 DTE', detail: 'Long enough for the breakdown to complete. LEAPs are appropriate here; very short-dated options have too little time.' },
        { rule: 'Ask ≤ 5% of stock price',    detail: 'Keeps cost-of-insurance sensible on names already in decline.' },
        { rule: 'Implied volatility ≤ 150%',  detail: 'Avoids puts on names where the market has already priced in the collapse.' },
        JC_SCORING,
        JC_TOP_10,
      ],
    },
  },
  {
    id:        'valuation-gravity',
    name:      'Valuation Gravity',
    shortName: 'Val. Gravity',
    tagline:   'Cheap puts on expensive stocks with decelerating growth',
    thesis:
      'Growth stocks priced to perfection are the most vulnerable when the underlying growth decelerates. The market is slow to reprice a deteriorating growth story — it clings to the narrative long after the numbers have turned. This scanner finds S&P 500 and NASDAQ 100 names trading above 15x trailing revenue with declining year-over-year revenue growth, and surfaces cheap OTM puts on them. The setup is a slow-burning compression trade.',
    icon: '⚖️',
    page: 'puts',

    judgementCalls: {
      intro: JC_INTRO,
      rules: [
        { rule: 'Universe',                   detail: 'S&P 500 and NASDAQ 100 constituents only.' },
        { rule: 'Price-to-sales above 15x',   detail: 'High revenue multiples leave no margin for error when growth slows. Below 15x the valuation compression thesis is weaker.' },
        { rule: 'Declining revenue growth',   detail: 'Year-over-year revenue growth must be positive but decelerating — the business is still growing, but slower than the market expects.' },
        { rule: 'Operating margin above -30%', detail: 'Excludes names already in financial distress. We want valuation compression, not insolvency risk.' },
        JC_OTM_PUTS,
        { rule: 'Expiry between 90 and 730 DTE', detail: 'Valuation compression is slow. LEAPs are the right instrument — give the thesis time to play out.' },
        { rule: 'Ask ≤ 5% of stock price',    detail: 'Cost discipline. Even on a slow-moving thesis, overpaying for premium destroys returns.' },
        { rule: 'Implied volatility ≤ 180%',  detail: 'Allows slightly higher IV given the longer timeframe, but avoids names where the market is already pricing in a crash.' },
        JC_SCORING,
        JC_TOP_10,
      ],
    },
  },
  // ── Calls themes ─────────────────────────────────────────────────────────
  {
    id:        'ai-momentum',
    name:      'AI Momentum (default)',
    shortName: 'AI Mom.',
    tagline:   'Cheap calls on AI and AI-adjacent names',
    thesis:
      'Macro tailwinds in AI, space, and disruptive tech create asymmetric upside in smaller, lesser-known names. This scanner finds tickers held across leading thematic ETFs — ARKK, ARKX, ARKQ, SMH, AIQ, BOTZ, and ROKT — that are showing strong 90-day momentum, and surfaces cheap out-of-the-money calls on them. The setup is a trend-continuation bet — small premium at risk, large payoff if the run extends.',
    icon: '🚀',
    page: 'calls',
    judgementCalls: {
      intro: JC_INTRO,
      rules: [
        { rule: 'Universe',                   detail: 'Tickers held across ARKK, ARKX, ARKQ, SMH, AIQ, BOTZ, and ROKT ETFs — a cross-section of AI, semiconductors, robotics, and space plays. Holdings are fetched daily via Yahoo Finance and cached.' },
        { rule: '15%+ momentum in 90 days',   detail: 'The ticker must be up at least 15% over the trailing 90 days. This confirms the trend is live before we look for calls.' },
        JC_OTM_CALLS,
        { rule: 'Expiry between 60 and 365 DTE', detail: 'Long enough for the thesis to play out. LEAPs are included — macro trends take time.' },
        { rule: 'Ask ≤ 4% of stock price',    detail: 'Keeps premium cost manageable. These are momentum names with naturally higher volatility, so we allow slightly more than the put scanner.' },
        { rule: 'Implied volatility ≤ 150%',  detail: 'High-momentum stocks carry high IV. We accept up to 150% — above that the market is already pricing in a parabolic move.' },
        JC_LIQUIDITY,
        JC_SCORING,
        JC_TOP_10,
      ],
    },
  },
  {
    id:        '52-week-breakouts',
    name:      '52-Week Breakouts',
    shortName: 'Breakouts',
    tagline:   'Cheap calls on stocks clearing 52-week highs',
    thesis:
      'Stocks breaking above their 52-week high on above-average volume are entering price discovery — prior resistance becomes support, and momentum tends to accelerate. This scanner finds S&P 500 and NASDAQ 100 names at or near fresh 52-week highs with volume confirmation, and surfaces cheap OTM calls on them. The setup is a trend-continuation bet with defined risk.',
    icon: '📈',
    page: 'calls',

    judgementCalls: {
      intro: JC_INTRO,
      rules: [
        { rule: 'Universe',                   detail: 'S&P 500 and NASDAQ 100 constituents only — liquid names where options markets are active.' },
        { rule: 'Within 2% of 52-week high',  detail: 'The stock must be within 2% of its trailing 52-week high, confirming it is in or near breakout territory.' },
        { rule: 'Volume confirmation',        detail: 'Today\'s volume must be at least 1.5× the 20-day average. Volume validates the breakout — without it, the move is suspect.' },
        JC_OTM_CALLS,
        { rule: 'Expiry between 30 and 180 DTE', detail: 'Long enough for the breakout to play out, short enough to preserve leverage. Longer-dated options lose too much to theta on a fast momentum trade.' },
        { rule: 'Ask ≤ 4% of stock price',    detail: 'Keeps premium cost manageable on high-momentum names.' },
        { rule: 'Implied volatility ≤ 120%',  detail: 'Avoids calls where the market has already priced in the move. Breakout names often see IV spike — we want to buy before that happens.' },
        JC_LIQUIDITY,
        JC_SCORING,
        JC_TOP_10,
      ],
    },
  },
  {
    id:        'short-squeeze',
    name:      'Short Squeeze',
    shortName: 'Squeeze',
    tagline:   'Cheap calls on high-short-interest names with upward momentum',
    thesis:
      'When a heavily-shorted stock starts moving up, short sellers are forced to cover — buying more shares and accelerating the move. This scanner identifies names with short interest above 15% of float that are also showing positive 30-day price momentum, and surfaces cheap OTM calls on them. The setup is asymmetric: if the squeeze triggers, the move is fast and violent.',
    icon: '🔥',
    page: 'calls',

    judgementCalls: {
      intro: JC_INTRO,
      rules: [
        { rule: 'Universe',                   detail: 'S&P 500 and NASDAQ 100 constituents only — large enough to have liquid options but heavily-shorted enough to squeeze.' },
        { rule: 'Short interest above 15% of float', detail: 'High short interest is the fuel. Below 15% there is not enough short interest to drive a meaningful squeeze.' },
        { rule: '10%+ momentum in 30 days',   detail: 'The stock must already be moving up — the squeeze must be in motion before we enter. This filters out value traps that are heavily-shorted for good reason.' },
        JC_OTM_CALLS,
        { rule: 'Expiry between 30 and 90 DTE', detail: 'Squeezes move fast. Shorter-dated options capture the explosive leg without paying for unnecessary theta.' },
        { rule: 'Ask ≤ 4% of stock price',    detail: 'Cost discipline — the squeeze either triggers quickly or it does not.' },
        { rule: 'Implied volatility ≤ 150%',  detail: 'Heavily-shorted names often carry elevated IV. Above 150% the market is already pricing in the squeeze.' },
        JC_LIQUIDITY,
        JC_SCORING,
        JC_TOP_10,
      ],
    },
  },
  {
    id:        'sector-rotation',
    name:      'Sector Rotation',
    shortName: 'Rotation',
    tagline:   'Cheap calls on leaders in the strongest sectors',
    thesis:
      'When capital rotates into a sector, the leading names in that sector move disproportionately. This scanner identifies which sectors are outperforming SPY over the trailing 30 days — using sector ETF holdings from XLK, XLE, XLF, XLI, XLV, and XLY — then surfaces cheap OTM calls on the strongest individual names within those sectors. The setup is a macro-rotation bet with individual-stock leverage.',
    icon: '🔄',
    page: 'calls',

    judgementCalls: {
      intro: JC_INTRO,
      rules: [
        { rule: 'Universe',                   detail: 'Holdings of sector ETFs: XLK (tech), XLE (energy), XLF (financials), XLI (industrials), XLV (healthcare), XLY (consumer discretionary). Holdings fetched via Yahoo Finance.' },
        { rule: 'Sector must outperform SPY by 5%+ over 30 days', detail: 'Only scan names in sectors with live rotation. Below 5% relative strength the rotation thesis is too weak.' },
        { rule: 'Stock in top 20% of sector by 30-day RS', detail: 'Within the outperforming sector, only the leaders qualify. Laggards in strong sectors still underperform.' },
        JC_OTM_CALLS,
        { rule: 'Expiry between 45 and 180 DTE', detail: 'Long enough for the rotation theme to sustain. Rotation cycles typically last 1–3 months.' },
        { rule: 'Ask ≤ 4% of stock price',    detail: 'Cost discipline — sector leaders carry higher IV than average names.' },
        { rule: 'Implied volatility ≤ 130%',  detail: 'Sector leaders in rotation can see IV spike quickly. Entering below 130% keeps the setup asymmetric.' },
        JC_LIQUIDITY,
        JC_SCORING,
        JC_TOP_10,
      ],
    },
  },
  {
    id:        'dram-memory',
    name:      'DRAM & Memory',
    shortName: 'Memory',
    tagline:   'Cheap calls on memory and storage names riding the HBM wave',
    thesis:
      'AI infrastructure demand has triggered a structural upcycle in memory. High-bandwidth memory (HBM) is sold out through 2026, DRAM pricing is recovering sharply, and memory fab equipment has a multi-year order backlog. This scanner watches Micron, Marvell, Western Digital, and the broader DRAM supply chain — fabs, equipment makers, and HBM-intensive server builders — for 30-day momentum, then surfaces cheap OTM calls on the names showing the strongest moves. The setup is a cycle-continuation bet: AI keeps scaling, memory keeps selling.',
    icon: '🧠',
    page: 'calls',

    judgementCalls: {
      intro: JC_INTRO,
      rules: [
        { rule: 'Universe',                   detail: 'A curated list of 13 DRAM and memory supply-chain names: MU, MRVL, WDC, SNDK, STX, LRCX, AMAT, KLAC, SMCI, INTC, ON, NXPI, MXL — covering pure-play DRAM, NAND (including SanDisk, spun off from WDC in 2025), HBM controllers, fab equipment, and HBM-intensive server systems.' },
        { rule: '10%+ momentum in 30 days',   detail: 'The name must be up at least 10% over the trailing 30 days, confirming the upcycle is live. Memory stocks move fast — a 30-day window captures the cycle better than a 90-day one.' },
        JC_OTM_CALLS,
        { rule: 'Expiry between 30 and 365 DTE', detail: 'Short enough to ride the current upcycle leg, long enough for the thesis to compound. LEAPs included for the structural bull case.' },
        { rule: 'Ask ≤ 5% of stock price',    detail: 'Memory and semi equipment names can carry elevated IV during upcycles. 5% keeps premium cost reasonable without excluding the best setups.' },
        { rule: 'Implied volatility ≤ 200%',  detail: 'Semi stocks can see extreme IV spikes during earnings and cycle inflection points. 200% filters out the most expensive premium while leaving most setups intact.' },
        JC_LIQUIDITY,
        JC_SCORING,
        JC_TOP_10,
      ],
    },
  },
  {
    id:        'space',
    name:      'Space',
    shortName: 'Space',
    tagline:   'Cheap calls on the new space economy',
    thesis:
      'The commercial space industry has hit an inflection point. Launch costs have collapsed, satellite broadband is scaling globally, and government contracts for lunar and deep-space missions are multiplying. This scanner watches pure-play names — Rocket Lab, AST SpaceMobile, Intuitive Machines, Planet Labs — alongside defence primes and satellite operators for 30-day momentum, then surfaces cheap OTM calls on the names showing the strongest moves. These stocks are volatile and thinly-priced relative to their optionality; when they run, they run hard.',
    icon: '🛸',
    page: 'calls',

    judgementCalls: {
      intro: JC_INTRO,
      rules: [
        { rule: 'Universe',                   detail: 'A curated list of 13 space-economy names: RKLB, ASTS, LUNR, PL, SPIR, KTOS, BWXT, RDW, LMT, NOC, GSAT, IRDM, SPCX — covering launch providers, satellite broadband, lunar services, earth observation, defence primes with major space divisions, and a space-economy basket.' },
        { rule: '10%+ momentum in 30 days',   detail: 'The name must be up at least 10% over the trailing 30 days. Space stocks can move violently on contract wins and launch milestones — a 30-day window captures those catalysts.' },
        JC_OTM_CALLS,
        { rule: 'Expiry between 30 and 365 DTE', detail: 'Long enough to span the next catalyst window, short enough to maintain leverage. LEAPs included for the longer-cycle thesis.' },
        { rule: 'Ask ≤ 5% of stock price',    detail: 'Space names — especially smaller pure-plays — carry structurally high IV. 5% cost cap keeps the setup asymmetric even on the most volatile names.' },
        { rule: 'Implied volatility ≤ 250%',  detail: 'ASTS, RKLB, and LUNR can see extreme IV around catalysts. 250% is a wide ceiling that captures most setups while excluding the most expensive post-catalyst premium.' },
        JC_LIQUIDITY,
        JC_SCORING,
        JC_TOP_10,
      ],
    },
  },
]

export function themesForPage(page: 'puts' | 'calls'): ThemeDefinition[] {
  return THEMES.filter(t => t.page === page)
}

export function themeById(id: string): ThemeDefinition | undefined {
  return THEMES.find(t => t.id === id)
}
