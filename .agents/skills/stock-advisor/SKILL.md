---
name: stock-advisor
description: >
  Generates an interactive HTML investment analysis report for any US stock ticker.
  Use this skill whenever the user provides a stock ticker symbol (like AAPL, TSLA, NVDA, GOOGL)
  and wants an investment opinion, analysis, or recommendation. Also triggers when the user asks
  "should I buy X stock", "analyze X for me", "what do legendary investors think of X", or any
  request combining a stock symbol with investment judgment. The skill runs a Python script that
  fetches real fundamental data via yfinance and produces a polished multi-perspective HTML report.
---

# Stock Advisor Skill

This skill generates a multi-perspective US stock investment report by analyzing real fundamental
data through the lenses of three legendary investors: Warren Buffett, Charlie Munger, and Duan Yongping.

## When to use this skill

- User provides a stock ticker and asks for an investment opinion or analysis
- User asks "should I buy [TICKER]?"
- User wants to know what value investors would think about a stock
- User asks for a fundamental analysis report on any US-listed company

## When NOT to use this skill

- The user is asking about crypto, forex, or non-US-listed stocks (yfinance coverage may be limited)
- The user only wants a price quote or simple lookup (no report needed)
- The user explicitly asks for technical analysis (chart patterns, moving averages) — this skill focuses on fundamentals only

## What the script does

The script `scripts/analyze_stock.py` accepts a ticker symbol, fetches live fundamental data
from Yahoo Finance via `yfinance`, and generates a self-contained interactive HTML report.

**Data fetched includes:**
- P/E ratio, Forward P/E, P/B ratio
- Return on Equity (ROE), Return on Assets (ROA)
- Profit margin, Operating margin
- Debt-to-Equity ratio
- Revenue growth (YoY), Earnings growth
- Free Cash Flow
- Current Ratio
- 52-week high/low, current price

**Three investor perspectives generated:**

1. **Warren Buffett** — Focuses on consistent earnings power, ROE > 15%, low debt, durable competitive moat, and whether the business is simple and understandable.
2. **Charlie Munger** — Focuses on business quality over price, mental models, whether the company has a "lollapalooza" of competitive advantages, and avoidance of complexity traps.
3. **Duan Yongping** — Focuses on the "right thing to do" business culture, whether the company has a genuine user mindset, long-term competitive position, and whether management acts like owners.

Each perspective produces a qualitative assessment and an overall signal (BUY / HOLD / PASS).

## How to use

Step 1: Install dependencies if not already present:
```bash
pip install yfinance --break-system-packages
```

Step 2: Run the script with a ticker symbol:
```bash
python scripts/analyze_stock.py AAPL
```

Step 3: The script outputs a file named `{TICKER}_report.html` in the current directory.
Open it in any browser — it is fully self-contained with no external dependencies.

## Expected output format

A single `{TICKER}_report.html` file containing:
- Company header with real-time price and key stats
- Three collapsible investor perspective cards (Buffett / Munger / Duan)
- A summary scorecard showing each investor's signal
- Color-coded metric table (green = strong, yellow = moderate, red = weak)

## Important limitations

- Data is sourced from Yahoo Finance and may have a short delay or missing fields for some tickers
- This report is for educational purposes only and does not constitute financial advice
- Analysis is rule-based, not a real investor's opinion
- Works best with large-cap US equities that have complete fundamental data on Yahoo Finance
