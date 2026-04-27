# Stock Advisor Skill

A reusable AI skill for Week 5: Build a Reusable AI Skill. It turns a US-listed stock ticker into a self-contained HTML fundamental analysis report using live Yahoo Finance data through `yfinance`.

Demo Video: https://youtu.be/piid1MhRoIs

## What The Skill Does

The skill helps an agent answer requests like "analyze AAPL" or "should I buy NVDA?" by running a deterministic Python script instead of trying to calculate financial ratios by hand. The script fetches company fundamentals, scores the stock through three investor lenses, and writes an interactive `{TICKER}_report.html` file.

The report includes:

- current price, sector, industry, market cap, 52-week range, and core valuation metrics
- profitability, growth, debt, liquidity, and free cash flow indicators
- separate Warren Buffett, Charlie Munger, and Duan Yongping style assessments
- BUY / HOLD / PASS signals with scored reasoning
- a bilingual Chinese / English interface and an educational disclaimer

## Repository Structure

```text
hw5-jiayizhuo/
├── README.md
├── .gitignore
└── .agents/
    └── skills/
        └── stock-advisor/
            ├── SKILL.md
            ├── requirements.txt
            └── scripts/
                └── analyze_stock.py
```

## How To Use It

Install the dependency and run the script from the skill folder:

```bash
cd .agents/skills/stock-advisor
python3 -m pip install -r requirements.txt
python3 scripts/analyze_stock.py AAPL
```

Open the generated report:

```bash
open AAPL_report.html
```

The HTML report is self-contained after generation, so it can be opened locally without a web server.

## Demo Prompts

Use these prompts to show the skill in an agent environment:

- Normal case: "Analyze AAPL and tell me whether it looks attractive from a long-term value investor perspective."
- Edge case: "Run the stock advisor for BRK-B and explain why some metrics may look different for Berkshire Hathaway."
- Failure case: "Analyze NOTATICKER and explain what happens when the ticker cannot be found."

## Why This Needs A Script

This task is load-bearing because the agent should not invent financial metrics or manually assemble HTML. The Python script handles the deterministic work: fetching structured data, applying scoring rules, formatting missing values, and generating the final report. The agent's role is to decide when the skill is relevant, run the script with the right ticker, and explain the output cautiously.

## Limitations

- This is for educational use only and is not financial advice.
- Data comes from Yahoo Finance through `yfinance`, so fields may be delayed, missing, or unavailable for some tickers.
- The skill is designed for US-listed equities, not crypto, forex, options, or private companies.
- The investor perspectives are rule-based approximations, not the actual views of Warren Buffett, Charlie Munger, or Duan Yongping.

## Verification Commands

```bash
python3 -m py_compile .agents/skills/stock-advisor/scripts/analyze_stock.py
cd .agents/skills/stock-advisor
python3 scripts/analyze_stock.py AAPL
python3 scripts/analyze_stock.py BRK-B
python3 scripts/analyze_stock.py NOTATICKER
```
