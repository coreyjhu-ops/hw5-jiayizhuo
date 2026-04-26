---
name: stock-advisor
description: >
  Generate an educational, rule-based HTML investment analysis report for a US-listed stock ticker.
  Use this skill when the user gives a ticker such as AAPL, TSLA, NVDA, GOOGL, or BRK-B and asks
  for fundamental analysis, a long-term value-investor view, or a cautious buy/hold/pass style
  discussion. The skill runs a Python script that fetches public Yahoo Finance data with yfinance
  and produces a self-contained report instead of inventing metrics in the model response.
---

# Stock Advisor Skill

This skill creates a reusable stock analysis workflow for US-listed equities. It runs a deterministic Python script that fetches public financial data, applies transparent scoring rules, and generates a self-contained HTML report through three investor lenses: Warren Buffett, Charlie Munger, and Duan Yongping.

## When to use this skill

- The user provides a US-listed stock ticker and asks for fundamental analysis.
- The user asks whether a stock looks attractive from a long-term or value-investing perspective.
- The user asks what Buffett, Munger, or Duan Yongping-style criteria would suggest.
- The user wants a reusable HTML report rather than a short price lookup.

## When NOT to use this skill

- The user asks about crypto, forex, options, bonds, private companies, or non-stock assets.
- The user only wants a current price quote or a simple company lookup.
- The user asks for technical analysis, chart patterns, day-trading signals, or short-term price prediction.
- The user asks for personalized financial advice. In that case, explain that the report is educational and not a recommendation.

## Script responsibility

Run `scripts/analyze_stock.py` with exactly one ticker symbol:

```bash
python3 scripts/analyze_stock.py AAPL
```

The script handles the deterministic part of the workflow:

- P/E ratio, Forward P/E, P/B ratio
- Return on Equity (ROE), Return on Assets (ROA)
- Profit margin, Operating margin
- Debt-to-Equity ratio
- Revenue growth (YoY), Earnings growth
- Free Cash Flow
- Current Ratio
- 52-week high/low, current price

It then creates `{TICKER}_report.html` in the current working directory.

## Investor lenses

- Warren Buffett: consistent earnings power, high ROE, low debt, durable business quality, and reasonable valuation.
- Charlie Munger: business quality, pricing power, capital efficiency, and avoidance of mediocre businesses.
- Duan Yongping: right business model, user mindset, owner-like management, healthy margins, and long-term patience.

Each lens produces a qualitative summary and a rule-based BUY / HOLD / PASS signal.

## Agent instructions

- Extract the ticker from the user request.
- If the ticker is ambiguous, ask one concise clarification question before running the script.
- Run the script from this skill folder after installing `requirements.txt` if needed.
- Tell the user where the generated HTML report was saved.
- Summarize the result cautiously and include the educational/non-financial-advice limitation.
- Do not present the output as personalized investment advice.

## Expected output

A single `{TICKER}_report.html` file containing:

- Company header with real-time price and key stats
- Three collapsible investor perspective cards (Buffett / Munger / Duan)
- A summary scorecard showing each investor's signal
- Color-coded metric table (green = strong, yellow = moderate, red = weak)
- Chinese / English language toggle

## Important limitations

- Data is sourced from Yahoo Finance and may be delayed or incomplete.
- Some tickers may fail if Yahoo Finance does not return usable data.
- The report is for educational purposes only and does not constitute financial advice.
- Analysis is rule-based and does not represent the real opinions of Buffett, Munger, or Duan Yongping.
- Works best with large-cap US equities that have complete Yahoo Finance coverage.
