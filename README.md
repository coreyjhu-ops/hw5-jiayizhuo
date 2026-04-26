# 📈 Stock Advisor Skill

A reusable AI skill that generates an interactive HTML investment analysis report for any US stock ticker — viewed through the investment philosophies of **Warren Buffett**, **Charlie Munger**, and **Duan Yongping (段永平)**.

🎥 **Demo Video**: [INSERT VIDEO LINK HERE]

---

## What it does

Input a stock ticker symbol → get a self-contained, interactive HTML report with:

- Real-time fundamental data (P/E, ROE, profit margins, debt, free cash flow, etc.)
- Three investor perspective cards with qualitative analysis in Chinese
- A BUY / HOLD / PASS signal from each investor lens
- Color-coded metrics table (green = strong, yellow = moderate, red = weak)
- Expandable company description and collapsible analysis cards

## Skill structure

```
stock-advisor/
├── SKILL.md              ← Skill instructions for the AI agent
└── scripts/
    └── analyze_stock.py  ← Core Python script (yfinance + HTML generator)
```

## Quick start

**1. Install dependency**
```bash
pip install yfinance
```

**2. Run the script**
```bash
python scripts/analyze_stock.py AAPL
```

**3. Open the report**
```bash
open AAPL_report.html   # macOS
```

The output is a fully self-contained HTML file — no internet connection needed to view it.

## Example tickers

```bash
python scripts/analyze_stock.py AAPL    # Apple
python scripts/analyze_stock.py TSLA    # Tesla
python scripts/analyze_stock.py BRK-B   # Berkshire Hathaway
python scripts/analyze_stock.py NVDA    # NVIDIA
python scripts/analyze_stock.py BIDU    # Baidu (US-listed)
```

## Investor frameworks

| Investor | Focus | Key Metrics |
|---|---|---|
| Warren Buffett | Consistent earnings, low debt, moat | ROE > 15%, margin, FCF, P/E |
| Charlie Munger | Business quality, pricing power | Operating margin, ROA, growth |
| 段永平 Duan Yongping | Right business model, owner mindset | Profit margin, ROE, debt, FCF |

## Limitations

- Data sourced from Yahoo Finance — may have short delays or missing fields for some tickers
- This report is for **educational purposes only** and does not constitute financial advice
- Best suited for large-cap US equities with complete Yahoo Finance coverage
- Analysis is rule-based, not the real opinions of these investors

## Tech stack

- Python 3.x
- [yfinance](https://github.com/ranaroussi/yfinance) — Yahoo Finance data
- Pure HTML/CSS/JS output (no external dependencies in the report)

---

*Built for JHU ISAI — Week 5: Build a Reusable AI Skill*
