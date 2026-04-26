#!/usr/bin/env python3
"""
Stock Advisor - Multi-Perspective Investment Analysis
Usage: python analyze_stock.py <TICKER>
Output: <TICKER>_report.html (self-contained interactive HTML report)
"""

import sys
import json
import datetime

try:
    import yfinance as yf
except ImportError:
    print("yfinance not found. Run: pip install yfinance --break-system-packages")
    sys.exit(1)


# ─────────────────────────────────────────────
#  Data Fetching
# ─────────────────────────────────────────────

def fetch_data(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    info = t.info

    def g(key, default=None):
        val = info.get(key, default)
        if val is None or val == "None":
            return default
        return val

    # Price & valuation
    price = g("currentPrice") or g("regularMarketPrice") or g("previousClose")
    pe = g("trailingPE")
    forward_pe = g("forwardPE")
    pb = g("priceToBook")
    ps = g("priceToSalesTrailing12Months")

    # Profitability
    roe = g("returnOnEquity")
    roa = g("returnOnAssets")
    profit_margin = g("profitMargins")
    operating_margin = g("operatingMargins")

    # Growth
    revenue_growth = g("revenueGrowth")
    earnings_growth = g("earningsGrowth")

    # Financial health
    debt_to_equity = g("debtToEquity")
    current_ratio = g("currentRatio")
    free_cashflow = g("freeCashflow")

    # Company info
    name = g("longName") or ticker.upper()
    sector = g("sector") or "N/A"
    industry = g("industry") or "N/A"
    summary = g("longBusinessSummary") or "No description available."
    week52_high = g("fiftyTwoWeekHigh")
    week52_low = g("fiftyTwoWeekLow")
    market_cap = g("marketCap")
    currency = g("currency") or "USD"
    employees = g("fullTimeEmployees")
    website = g("website") or ""
    dividend_yield = g("dividendYield")
    beta = g("beta")

    return {
        "ticker": ticker.upper(),
        "name": name,
        "sector": sector,
        "industry": industry,
        "summary": summary,
        "currency": currency,
        "website": website,
        "employees": employees,
        "price": price,
        "week52_high": week52_high,
        "week52_low": week52_low,
        "market_cap": market_cap,
        "pe": pe,
        "forward_pe": forward_pe,
        "pb": pb,
        "ps": ps,
        "roe": roe,
        "roa": roa,
        "profit_margin": profit_margin,
        "operating_margin": operating_margin,
        "revenue_growth": revenue_growth,
        "earnings_growth": earnings_growth,
        "debt_to_equity": debt_to_equity,
        "current_ratio": current_ratio,
        "free_cashflow": free_cashflow,
        "dividend_yield": dividend_yield,
        "beta": beta,
    }


# ─────────────────────────────────────────────
#  Analysis Engines
# ─────────────────────────────────────────────

def fmt_pct(val):
    if val is None:
        return "N/A"
    return f"{val * 100:.1f}%"

def fmt_num(val, decimals=2):
    if val is None:
        return "N/A"
    return f"{val:.{decimals}f}"

def fmt_large(val):
    if val is None:
        return "N/A"
    if abs(val) >= 1e12:
        return f"${val/1e12:.2f}T"
    if abs(val) >= 1e9:
        return f"${val/1e9:.2f}B"
    if abs(val) >= 1e6:
        return f"${val/1e6:.2f}M"
    return f"${val:,.0f}"


def analyze_buffett(d: dict) -> dict:
    """
    Buffett style: consistent earnings, high ROE, low debt, understandable business,
    reasonable valuation, strong free cash flow.
    """
    score = 0
    max_score = 0
    points_zh = []
    warnings_zh = []
    points_en = []
    warnings_en = []

    # ROE > 15%
    max_score += 2
    if d["roe"] is not None:
        if d["roe"] > 0.20:
            score += 2
            points_zh.append("✅ ROE超过20%，体现出强大的股东回报能力，是Buffett最看重的护城河信号之一。")
            points_en.append("✅ ROE exceeds 20%, demonstrating strong shareholder returns — one of Buffett's top moat signals.")
        elif d["roe"] > 0.15:
            score += 1
            points_zh.append("🟡 ROE在15%-20%之间，尚可接受，但不够突出。")
            points_en.append("🟡 ROE is between 15%–20%, acceptable but not exceptional.")
        else:
            warnings_zh.append("❌ ROE低于15%，表明资本回报率不足，Buffett通常会回避此类企业。")
            warnings_en.append("❌ ROE is below 15%, indicating weak capital returns — Buffett typically avoids such companies.")
    else:
        warnings_zh.append("⚠️ ROE数据缺失，无法评估资本回报质量。")
        warnings_en.append("⚠️ ROE data unavailable — cannot assess capital return quality.")

    # Profit margin > 15%
    max_score += 2
    if d["profit_margin"] is not None:
        if d["profit_margin"] > 0.20:
            score += 2
            points_zh.append("✅ 净利润率超过20%，说明企业具备强定价权和成本控制能力。")
            points_en.append("✅ Net profit margin exceeds 20%, showing strong pricing power and cost discipline.")
        elif d["profit_margin"] > 0.10:
            score += 1
            points_zh.append("🟡 净利润率在10%-20%之间，盈利质量中等。")
            points_en.append("🟡 Net margin between 10%–20% — moderate profitability quality.")
        else:
            warnings_zh.append("❌ 净利润率低于10%，盈利能力薄弱，不符合Buffett的选股标准。")
            warnings_en.append("❌ Net margin below 10% — weak earnings power, does not meet Buffett's standard.")
    else:
        warnings_zh.append("⚠️ 净利润率数据缺失。")
        warnings_en.append("⚠️ Net profit margin data unavailable.")

    # Debt-to-equity < 50
    max_score += 2
    if d["debt_to_equity"] is not None:
        de = d["debt_to_equity"]
        if de < 50:
            score += 2
            points_zh.append("✅ 负债权益比极低，财务结构稳健，抗风险能力强。")
            points_en.append("✅ Very low debt-to-equity ratio — solid financial structure with strong resilience.")
        elif de < 100:
            score += 1
            points_zh.append("🟡 负债权益比适中，需持续关注偿债压力。")
            points_en.append("🟡 Moderate debt-to-equity — worth monitoring debt repayment pressure.")
        else:
            warnings_zh.append("❌ 高负债权益比意味着财务风险较高，Buffett倾向于避开重债企业。")
            warnings_en.append("❌ High debt-to-equity signals financial risk — Buffett avoids heavily leveraged companies.")
    else:
        warnings_zh.append("⚠️ 负债率数据缺失。")
        warnings_en.append("⚠️ Debt-to-equity data unavailable.")

    # Free cash flow positive
    max_score += 2
    if d["free_cashflow"] is not None:
        if d["free_cashflow"] > 0:
            score += 2
            points_zh.append("✅ 自由现金流为正，企业能持续产生真实现金，是Buffett判断企业质量的核心指标。")
            points_en.append("✅ Positive free cash flow — the company generates real cash, a core Buffett quality indicator.")
        else:
            warnings_zh.append("❌ 自由现金流为负，企业尚未达到Buffett要求的'印钞机'标准。")
            warnings_en.append("❌ Negative free cash flow — falls short of Buffett's 'money machine' standard.")
    else:
        warnings_zh.append("⚠️ 自由现金流数据缺失。")
        warnings_en.append("⚠️ Free cash flow data unavailable.")

    # P/E reasonable
    max_score += 2
    if d["pe"] is not None:
        if d["pe"] < 15:
            score += 2
            points_zh.append("✅ 市盈率低于15倍，估值合理，存在安全边际。")
            points_en.append("✅ P/E ratio below 15x — reasonable valuation with a margin of safety.")
        elif d["pe"] < 25:
            score += 1
            points_zh.append("🟡 市盈率在15-25倍之间，估值偏高但尚在可接受范围。")
            points_en.append("🟡 P/E between 15–25x — somewhat elevated but within acceptable range.")
        else:
            warnings_zh.append("❌ 市盈率超过25倍，Buffett会要求更强的确定性才愿意以此价格买入。")
            warnings_en.append("❌ P/E exceeds 25x — Buffett would demand much higher certainty to justify this price.")
    else:
        warnings_zh.append("⚠️ 市盈率数据缺失，无法评估估值安全边际。")
        warnings_en.append("⚠️ P/E data unavailable — cannot assess valuation margin of safety.")

    ratio = score / max_score if max_score > 0 else 0
    if ratio >= 0.75:
        signal = "BUY"
        signal_color = "#22c55e"
        summary_zh = f"从Buffett的视角看，{d['name']}是一家高质量企业。它拥有稳定的盈利能力、合理的财务结构，符合'以合理价格买入优秀企业'的核心原则。长期持有的理由充分。"
        summary_en = f"From Buffett's perspective, {d['name']} is a high-quality business. It shows consistent earnings power and a sound financial structure — perfectly aligned with his core principle of buying wonderful companies at fair prices. Strong case for long-term holding."
    elif ratio >= 0.5:
        signal = "HOLD"
        signal_color = "#f59e0b"
        summary_zh = f"该企业具备部分Buffett所看重的特质，但仍有不足。Buffett可能会将其列入观察名单，等待更好的买入时机或更低的估值。"
        summary_en = f"The company shows some qualities Buffett values, but falls short in key areas. He would likely add it to a watchlist, waiting for a better entry point or lower valuation."
    else:
        signal = "PASS"
        signal_color = "#ef4444"
        summary_zh = f"从Buffett的标准来看，该企业在盈利质量、负债或估值方面存在明显短板。Buffett的名言是'宁可错过，也不要犯错'，这类企业他会直接跳过。"
        summary_en = f"By Buffett's standards, this company has notable weaknesses in earnings quality, debt load, or valuation. As he says, 'It's better to miss an opportunity than to make a mistake.' He would pass."

    return {
        "name": "Warren Buffett",
        "avatar": "🎩",
        "tagline_zh": "以合理价格买入优秀企业，然后永远持有",
        "tagline_en": "Buy wonderful companies at fair prices, then hold forever",
        "signal": signal,
        "signal_color": signal_color,
        "summary_zh": summary_zh,
        "summary_en": summary_en,
        "points_zh": points_zh,
        "warnings_zh": warnings_zh,
        "points_en": points_en,
        "warnings_en": warnings_en,
        "score": score,
        "max_score": max_score,
    }


def analyze_munger(d: dict) -> dict:
    """
    Munger style: business quality above all, mental models, moat, avoid mediocrity,
    look for lollapalooza effects, margin of safety in quality not just price.
    """
    score = 0
    max_score = 0
    points_zh = []
    warnings_zh = []
    points_en = []
    warnings_en = []

    # Operating margin > 20% = pricing power
    max_score += 2
    if d["operating_margin"] is not None:
        if d["operating_margin"] > 0.25:
            score += 2
            points_zh.append("✅ 营业利润率超过25%，体现出极强的定价权，是Munger所称'护城河'的最直接财务体现。")
            points_en.append("✅ Operating margin exceeds 25% — strong pricing power, the most direct financial proof of a moat.")
        elif d["operating_margin"] > 0.15:
            score += 1
            points_zh.append("🟡 营业利润率在15%-25%，具备一定竞争优势，但护城河深度有待验证。")
            points_en.append("🟡 Operating margin 15%–25% — some competitive edge, but moat depth needs verification.")
        else:
            warnings_zh.append("❌ 营业利润率偏低，说明企业缺乏真正的定价权，Munger会将其归类为'平庸企业'。")
            warnings_en.append("❌ Low operating margin signals a lack of real pricing power — Munger would call this a 'mediocre business.'")
    else:
        warnings_zh.append("⚠️ 营业利润率数据缺失。")
        warnings_en.append("⚠️ Operating margin data unavailable.")

    # ROA > 8% = asset efficiency
    max_score += 2
    if d["roa"] is not None:
        if d["roa"] > 0.12:
            score += 2
            points_zh.append("✅ 资产回报率(ROA)超过12%，说明企业用资产高效创造价值，是Munger'好生意'的标志。")
            points_en.append("✅ ROA exceeds 12% — assets are working hard to create value, a hallmark of Munger's 'good business.'")
        elif d["roa"] > 0.06:
            score += 1
            points_zh.append("🟡 ROA在6%-12%之间，资产效率一般。")
            points_en.append("🟡 ROA between 6%–12% — average asset efficiency.")
        else:
            warnings_zh.append("❌ ROA低于6%，资产转化盈利效率低，Munger通常不会对这类企业感兴趣。")
            warnings_en.append("❌ ROA below 6% — poor asset-to-profit conversion, Munger would typically lose interest.")
    else:
        warnings_zh.append("⚠️ ROA数据缺失。")
        warnings_en.append("⚠️ ROA data unavailable.")

    # Revenue growth > 5%
    max_score += 2
    if d["revenue_growth"] is not None:
        if d["revenue_growth"] > 0.15:
            score += 2
            points_zh.append("✅ 收入增速超过15%，企业正处于价值积累的加速阶段。")
            points_en.append("✅ Revenue growing over 15% — the company is in an accelerating value-creation phase.")
        elif d["revenue_growth"] > 0.05:
            score += 1
            points_zh.append("🟡 收入保持稳定增长，企业能维持市场地位。")
            points_en.append("🟡 Stable revenue growth — the company is holding its market position.")
        else:
            warnings_zh.append("❌ 收入增速低迷，可能意味着行业天花板已近或竞争力下滑。")
            warnings_en.append("❌ Sluggish revenue growth — may signal an approaching industry ceiling or weakening competitiveness.")
    else:
        warnings_zh.append("⚠️ 收入增速数据缺失。")
        warnings_en.append("⚠️ Revenue growth data unavailable.")

    # P/B < 5 for quality business
    max_score += 2
    if d["pb"] is not None:
        if d["pb"] < 3:
            score += 2
            points_zh.append("✅ 市净率低于3倍，账面价值相对合理，有一定安全边际。")
            points_en.append("✅ P/B ratio below 3x — book value is reasonably priced with a safety margin.")
        elif d["pb"] < 8:
            score += 1
            points_zh.append("🟡 市净率在3-8倍，溢价在高质量企业中可以接受，但需要强大的护城河作为支撑。")
            points_en.append("🟡 P/B between 3–8x — premium is acceptable for quality businesses, but requires a strong moat.")
        else:
            warnings_zh.append("❌ 市净率过高，即便是高质量企业，过高的溢价也会压缩未来回报。")
            warnings_en.append("❌ P/B too high — even for quality companies, excessive premiums compress future returns.")
    else:
        warnings_zh.append("⚠️ 市净率数据缺失。")
        warnings_en.append("⚠️ P/B data unavailable.")

    # Free cash flow
    max_score += 2
    if d["free_cashflow"] is not None:
        if d["free_cashflow"] > 0:
            score += 2
            points_zh.append("✅ 自由现金流为正，企业不依赖持续融资即可运营，体现出真正的商业价值。")
            points_en.append("✅ Positive free cash flow — the business runs without needing constant financing, showing real commercial value.")
        else:
            warnings_zh.append("❌ 自由现金流为负，Munger会问：这门生意的钱到底去哪了？")
            warnings_en.append("❌ Negative free cash flow — Munger would ask: where is all the money actually going?")
    else:
        warnings_zh.append("⚠️ 自由现金流数据缺失。")
        warnings_en.append("⚠️ Free cash flow data unavailable.")

    ratio = score / max_score if max_score > 0 else 0
    if ratio >= 0.75:
        signal = "BUY"
        signal_color = "#22c55e"
        summary_zh = f"Munger会称这家企业为'wonderful company'。它在定价权、资本效率和现金流上均展现出卓越品质。Munger的哲学是：宁可高价买好货，也不低价买烂货——而这家企业值得认真考虑。"
        summary_en = f"Munger would call this a 'wonderful company.' It excels in pricing power, capital efficiency, and cash flow. His philosophy: better to pay a fair price for a great business than a low price for a mediocre one — and this company deserves serious consideration."
    elif ratio >= 0.5:
        signal = "HOLD"
        signal_color = "#f59e0b"
        summary_zh = f"该企业具备部分优秀特质，但在某些关键维度上尚未达到Munger的'lollapalooza'标准。他可能会说：'这是一家不错的企业，但不是我梦寐以求的那种。'"
        summary_en = f"The company has some admirable qualities but hasn't reached Munger's 'lollapalooza' standard in key areas. He might say: 'It's a decent business — just not the kind I dream about.'"
    else:
        signal = "PASS"
        signal_color = "#ef4444"
        summary_zh = f"Munger对平庸企业深恶痛绝。他的名言是'反过来想，总是反过来想'——如果一家企业有这么多短板，你应该问的不是'该不该买'，而是'我为什么还在考虑它'。"
        summary_en = f"Munger has deep contempt for mediocre businesses. His motto: 'Invert, always invert.' If a company has this many weaknesses, don't ask 'should I buy it?' — ask 'why am I still thinking about it?'"

    return {
        "name": "Charlie Munger",
        "avatar": "🧠",
        "tagline_zh": "反过来想，总是反过来想",
        "tagline_en": "Invert, always invert",
        "signal": signal,
        "signal_color": signal_color,
        "summary_zh": summary_zh,
        "summary_en": summary_en,
        "points_zh": points_zh,
        "warnings_zh": warnings_zh,
        "points_en": points_en,
        "warnings_en": warnings_en,
        "score": score,
        "max_score": max_score,
    }


def analyze_duan(d: dict) -> dict:
    """
    Duan Yongping style: do the right thing, long-term, user mindset,
    business model clarity, stop doing list, management integrity.
    """
    score = 0
    max_score = 0
    points_zh = []
    warnings_zh = []
    points_en = []
    warnings_en = []

    # High profit margin = good business model
    max_score += 2
    if d["profit_margin"] is not None:
        if d["profit_margin"] > 0.15:
            score += 2
            points_zh.append("✅ 高净利润率说明这门生意本身就是正确的——用户愿意为产品溢价买单，商业模式清晰健康。")
            points_en.append("✅ High net margin shows this is the right business — users pay a premium willingly, and the model is clean and healthy.")
        elif d["profit_margin"] > 0.05:
            score += 1
            points_zh.append("🟡 利润率尚可，但段永平会问：这个利润是靠效率得来的，还是靠压榨供应商/员工得来的？")
            points_en.append("🟡 Margins are acceptable, but Duan would ask: is this profit from efficiency, or from squeezing suppliers and workers?")
        else:
            warnings_zh.append("❌ 利润率过低说明这门生意可能不是'对的事情'，段永平会直接说：Stop doing it。")
            warnings_en.append("❌ Margins too thin — this business may not be the 'right thing to do.' Duan would say: stop doing it.")
    else:
        warnings_zh.append("⚠️ 利润率数据缺失，无法判断商业模式是否健康。")
        warnings_en.append("⚠️ Margin data unavailable — cannot assess business model health.")

    # Revenue growth consistency
    max_score += 2
    if d["revenue_growth"] is not None:
        if d["revenue_growth"] > 0.10:
            score += 2
            points_zh.append("✅ 收入持续增长，说明企业真的在为用户创造价值，市场在用钱投票。")
            points_en.append("✅ Sustained revenue growth shows the company is genuinely creating user value — the market is voting with money.")
        elif d["revenue_growth"] > 0:
            score += 1
            points_zh.append("🟡 收入缓慢增长，企业尚在维持，但段永平会担心增长动力是否可持续。")
            points_en.append("🟡 Slow but positive revenue growth — the company is holding on, but Duan would question whether momentum is sustainable.")
        else:
            warnings_zh.append("❌ 收入下滑是一个严重信号。段永平认为，一家真正以用户为中心的企业不应该长期萎缩。")
            warnings_en.append("❌ Declining revenue is a serious warning. A truly user-focused company should not shrink over the long term.")
    else:
        warnings_zh.append("⚠️ 收入增速数据缺失。")
        warnings_en.append("⚠️ Revenue growth data unavailable.")

    # ROE: owner mindset
    max_score += 2
    if d["roe"] is not None:
        if d["roe"] > 0.18:
            score += 2
            points_zh.append("✅ 高ROE反映出管理层像真正的股东一样经营公司，而不是只会花股东的钱。")
            points_en.append("✅ High ROE shows management operates like true owners — not just spending shareholders' money.")
        elif d["roe"] > 0.10:
            score += 1
            points_zh.append("🟡 ROE处于中等水平，管理层资本配置能力有待提高。")
            points_en.append("🟡 Moderate ROE — management's capital allocation skills have room to improve.")
        else:
            warnings_zh.append("❌ 低ROE意味着管理层可能在低效使用股东资产，这与段永平'做对的事'的理念相违背。")
            warnings_en.append("❌ Low ROE suggests management may be using shareholder assets inefficiently — contrary to Duan's 'do the right thing' philosophy.")
    else:
        warnings_zh.append("⚠️ ROE数据缺失。")
        warnings_en.append("⚠️ ROE data unavailable.")

    # Debt: avoid over-leverage
    max_score += 2
    if d["debt_to_equity"] is not None:
        de = d["debt_to_equity"]
        if de < 60:
            score += 2
            points_zh.append("✅ 负债率低，说明企业不靠借钱来维持增长，这与段永平'做对的事'中的'不赌博'原则一致。")
            points_en.append("✅ Low debt ratio — the company grows without borrowing, consistent with Duan's 'don't gamble' principle.")
        elif de < 150:
            score += 1
            points_zh.append("🟡 负债率中等，需关注是否存在过度扩张的冲动。")
            points_en.append("🟡 Moderate debt — watch for signs of overexpansion ambitions.")
        else:
            warnings_zh.append("❌ 高负债是段永平明确反对的，他认为真正好的生意不需要靠杠杆来驱动。")
            warnings_en.append("❌ Heavy debt is something Duan explicitly opposes — truly great businesses don't need leverage to grow.")
    else:
        warnings_zh.append("⚠️ 负债率数据缺失。")
        warnings_en.append("⚠️ Debt ratio data unavailable.")

    # Free cashflow: real business
    max_score += 2
    if d["free_cashflow"] is not None:
        if d["free_cashflow"] > 0:
            score += 2
            points_zh.append("✅ 正向自由现金流证明这是一门真实的生意——不是靠融资续命的故事。")
            points_en.append("✅ Positive free cash flow proves this is a real business — not a story that only survives on constant fundraising.")
        else:
            warnings_zh.append("❌ 自由现金流为负，段永平会问：这门生意的终局到底是什么？")
            warnings_en.append("❌ Negative free cash flow — Duan would ask: what is the actual endgame of this business?")
    else:
        warnings_zh.append("⚠️ 自由现金流数据缺失。")
        warnings_en.append("⚠️ Free cash flow data unavailable.")

    ratio = score / max_score if max_score > 0 else 0
    if ratio >= 0.75:
        signal = "BUY"
        signal_color = "#22c55e"
        summary_zh = f"段永平会认为{d['name']}是一门'对的生意'。它盈利健康、增长真实、负债合理，管理层体现出股东思维。他的投资哲学强调'做对的事，然后等待'——这类企业值得长期持有。"
        summary_en = f"Duan would see {d['name']} as the 'right kind of business.' Healthy profits, real growth, sensible debt, and management with an owner's mindset. His philosophy: 'Do the right thing, then wait.' This company is worth holding long-term."
    elif ratio >= 0.5:
        signal = "HOLD"
        signal_color = "#f59e0b"
        summary_zh = f"该企业有一定价值，但还未达到段永平'一眼胖瘦'的标准。他可能会说：先放着，继续观察企业文化和管理层的行为，再做决定。"
        summary_en = f"The company has merit, but hasn't reached Duan's 'obvious at a glance' standard. He might say: set it aside, keep watching the company culture and management behavior before deciding."
    else:
        signal = "PASS"
        signal_color = "#ef4444"
        summary_zh = f"段永平的'Stop Doing List'里有一条：远离那些你看不懂、或者不赚钱的生意。对于这家企业，他会选择直接跳过，把时间留给更值得等待的机会。"
        summary_en = f"Duan's 'Stop Doing List' has one clear rule: stay away from businesses you don't understand or that don't make money. He would skip this one entirely and save his patience for something more deserving."

    return {
        "name": "段永平 Duan Yongping",
        "avatar": "🎯",
        "tagline_zh": "做对的事，然后把事情做对",
        "tagline_en": "Do the right thing, then do things right",
        "signal": signal,
        "signal_color": signal_color,
        "summary_zh": summary_zh,
        "summary_en": summary_en,
        "points_zh": points_zh,
        "warnings_zh": warnings_zh,
        "points_en": points_en,
        "warnings_en": warnings_en,
        "score": score,
        "max_score": max_score,
    }


# ─────────────────────────────────────────────
#  HTML Generator
# ─────────────────────────────────────────────

def metric_color(val, low_bad=True, thresholds=(0.1, 0.2)):
    """Return a CSS class for a metric value."""
    if val is None:
        return "metric-na"
    lo, hi = thresholds
    if low_bad:
        if val >= hi:
            return "metric-good"
        elif val >= lo:
            return "metric-mid"
        else:
            return "metric-bad"
    else:
        if val <= lo:
            return "metric-good"
        elif val <= hi:
            return "metric-mid"
        else:
            return "metric-bad"


def generate_html(d: dict, analyses: list) -> str:
    ticker = d["ticker"]
    name = d["name"]
    price = f"${d['price']:.2f}" if d["price"] else "N/A"
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Key metrics table rows — label pairs (zh, en) + value info
    de_class = ""
    if d["debt_to_equity"] is not None:
        de_class = "metric-good" if d["debt_to_equity"] < 50 else ("metric-mid" if d["debt_to_equity"] < 100 else "metric-bad")

    roe_class = metric_color(d["roe"], True, (0.10, 0.20))
    pm_class = metric_color(d["profit_margin"], True, (0.08, 0.18))
    om_class = metric_color(d["operating_margin"], True, (0.10, 0.20))
    roa_class = metric_color(d["roa"], True, (0.05, 0.12))
    rg_class = metric_color(d["revenue_growth"], True, (0.03, 0.12))

    def fmt_val(val, fmt):
        if val is None:
            return "N/A"
        if fmt == "pct":
            return fmt_pct(val)
        if fmt == "num":
            return fmt_num(val)
        if fmt == "large":
            return fmt_large(val)
        return str(val)

    metric_rows = [
        ("当前股价", "Current Price",       f"${d['price']:.2f}" if d['price'] else "N/A", ""),
        ("市值",     "Market Cap",          fmt_val(d['market_cap'], "large"),              ""),
        ("52周最高", "52-Week High",        f"${d['week52_high']:.2f}" if d['week52_high'] else "N/A", ""),
        ("52周最低", "52-Week Low",         f"${d['week52_low']:.2f}" if d['week52_low'] else "N/A",  ""),
        ("市盈率 (TTM)", "P/E (TTM)",       fmt_val(d['pe'], "num"),                        ""),
        ("远期市盈率",   "Forward P/E",     fmt_val(d['forward_pe'], "num"),                ""),
        ("市净率",       "P/B Ratio",       fmt_val(d['pb'], "num"),                        ""),
        ("市销率",       "P/S Ratio",       fmt_val(d['ps'], "num"),                        ""),
        ("股本回报率 ROE", "ROE",           fmt_val(d['roe'], "pct"),                       roe_class),
        ("资产回报率 ROA", "ROA",           fmt_val(d['roa'], "pct"),                       roa_class),
        ("净利润率",     "Net Margin",      fmt_val(d['profit_margin'], "pct"),             pm_class),
        ("营业利润率",   "Operating Margin",fmt_val(d['operating_margin'], "pct"),          om_class),
        ("收入增速 (YoY)", "Revenue Growth",fmt_val(d['revenue_growth'], "pct"),            rg_class),
        ("盈利增速 (YoY)", "Earnings Growth",fmt_val(d['earnings_growth'], "pct"),          ""),
        ("负债权益比",   "Debt/Equity",     fmt_val(d['debt_to_equity'], "num"),            de_class),
        ("流动比率",     "Current Ratio",   fmt_val(d['current_ratio'], "num"),             ""),
        ("自由现金流",   "Free Cash Flow",  fmt_val(d['free_cashflow'], "large"),           ""),
        ("股息率",       "Dividend Yield",  fmt_val(d['dividend_yield'], "pct"),            ""),
        ("Beta",         "Beta",            fmt_val(d['beta'], "num"),                      ""),
    ]

    metrics_rows_html = ""
    for zh_lbl, en_lbl, val, cls in metric_rows:
        metrics_rows_html += f'<tr><td><span data-zh="{zh_lbl}" data-en="{en_lbl}">{zh_lbl}</span></td><td class="{cls}">{val}</td></tr>\n'

    # Build JS data payload for bilingual switching
    js_analyses = []
    for a in analyses:
        js_analyses.append({
            "tagline_zh": a["tagline_zh"],
            "tagline_en": a["tagline_en"],
            "summary_zh": a["summary_zh"],
            "summary_en": a["summary_en"],
            "points_zh":  a["points_zh"],
            "points_en":  a["points_en"],
            "warnings_zh": a["warnings_zh"],
            "warnings_en": a["warnings_en"],
        })
    js_data = json.dumps(js_analyses, ensure_ascii=False)

    # Hero meta employees string
    employees_html = f'<span>👥 <span data-zh="{d["employees"]:,} 名员工" data-en="{d["employees"]:,} employees">{d["employees"]:,} 名员工</span></span>' if d.get("employees") else ""
    website_html = f'<span>🌐 <a href="{d["website"]}" style="color:var(--accent)" target="_blank">{d["website"]}</a></span>' if d.get("website") else ""

    # Scorecard
    scorecard_html = ""
    for a in analyses:
        scorecard_html += f"""
        <div class="score-card">
            <span class="score-avatar">{a['avatar']}</span>
            <div class="score-name">{a['name']}</div>
            <div class="score-signal" style="color:{a['signal_color']};border-color:{a['signal_color']}">{a['signal']}</div>
            <div class="score-ratio">{a['score']}/{a['max_score']} pts</div>
        </div>"""

    # Investor panels (static skeleton; text swapped by JS)
    panels_html = ""
    for i, a in enumerate(analyses):
        pct = int(a['score'] / a['max_score'] * 100) if a['max_score'] else 0
        panels_html += f"""
        <div class="investor-card" id="card-{i}">
            <div class="card-header" onclick="toggleCard({i})">
                <div class="card-title">
                    <span class="card-avatar">{a['avatar']}</span>
                    <div>
                        <div class="card-name">{a['name']}</div>
                        <div class="card-tagline" id="tagline-{i}">"{a['tagline_zh']}"</div>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:12px">
                    <div class="signal-badge" style="background:{a['signal_color']}">{a['signal']}</div>
                    <div class="card-chevron" id="chevron-{i}">▼</div>
                </div>
            </div>
            <div class="card-body" id="body-{i}">
                <div class="card-summary" id="summary-{i}">{a['summary_zh']}</div>
                <div class="two-col">
                    <div>
                        <div class="col-title" id="col-pros-title-{i}">✅ 优势因素</div>
                        <ul class="point-list" id="pros-{i}">
                            {''.join(f"<li>{p}</li>" for p in a['points_zh']) if a['points_zh'] else '<li style="color:#94a3b8" id="no-pros-{i}">暂无明显优势</li>'}
                        </ul>
                    </div>
                    <div>
                        <div class="col-title" id="col-cons-title-{i}">⚠️ 风险因素</div>
                        <ul class="point-list" id="cons-{i}">
                            {''.join(f"<li>{w}</li>" for w in a['warnings_zh']) if a['warnings_zh'] else '<li style="color:#94a3b8" id="no-cons-{i}">暂无明显风险</li>'}
                        </ul>
                    </div>
                </div>
                <div class="progress-bar-wrap">
                    <div class="progress-label" id="score-label-{i}">综合评分</div>
                    <div class="progress-track">
                        <div class="progress-fill" style="width:{pct}%;background:{a['signal_color']}"></div>
                    </div>
                    <div class="progress-pct">{pct}%</div>
                </div>
            </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{ticker} — Investment Analysis Report</title>
<style>
  :root {{
    --bg: #0f172a;
    --surface: #1e293b;
    --surface2: #334155;
    --border: #475569;
    --text: #f1f5f9;
    --muted: #94a3b8;
    --accent: #6366f1;
    --good: #22c55e;
    --mid: #f59e0b;
    --bad: #ef4444;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: var(--bg); color: var(--text); min-height: 100vh; }}

  /* Language toggle */
  .lang-toggle {{
    position: fixed; top: 16px; right: 20px; z-index: 999;
    display: flex; background: var(--surface2); border: 1px solid var(--border);
    border-radius: 24px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.4);
  }}
  .lang-btn {{
    padding: 8px 18px; font-size: 13px; font-weight: 700; cursor: pointer;
    border: none; background: transparent; color: var(--muted);
    transition: background .2s, color .2s; letter-spacing: .5px;
  }}
  .lang-btn.active {{
    background: var(--accent); color: white; border-radius: 24px;
  }}

  /* Hero */
  .hero {{ background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 60%);
           border-bottom: 1px solid var(--border); padding: 40px 32px 32px; }}
  .hero-inner {{ max-width: 1100px; margin: 0 auto; }}
  .hero-top {{ display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px; }}
  .ticker-badge {{ font-size: 14px; font-weight:700; color:var(--accent);
                   background: rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.3);
                   padding: 4px 12px; border-radius:20px; letter-spacing:1px; }}
  .company-name {{ font-size: 32px; font-weight:800; margin: 8px 0 4px; }}
  .company-meta {{ color:var(--muted); font-size:14px; display:flex; gap:16px; flex-wrap:wrap; }}
  .price-block {{ text-align:right; }}
  .price-num {{ font-size:40px; font-weight:800; color:white; }}
  .price-label {{ color:var(--muted); font-size:12px; margin-top:4px; }}
  .date-tag {{ color:var(--muted); font-size:12px; margin-top:24px; }}
  .disclaimer {{ background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.3);
                 border-radius:8px; padding:10px 16px; font-size:12px; color:#fbbf24; margin-top:16px; }}

  /* Scorecard */
  .scorecard {{ display:flex; gap:16px; flex-wrap:wrap; margin:32px 0; }}
  .score-card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px;
                 padding:20px; flex:1; min-width:160px; text-align:center; }}
  .score-avatar {{ font-size:28px; }}
  .score-name {{ font-size:13px; font-weight:600; color:var(--text); margin:8px 0 6px; }}
  .score-signal {{ font-size:20px; font-weight:900; border:2px solid; border-radius:8px;
                   padding:4px 16px; display:inline-block; margin:4px 0; }}
  .score-ratio {{ font-size:12px; color:var(--muted); margin-top:6px; }}

  /* Main layout */
  .main {{ max-width:1100px; margin:0 auto; padding:32px; display:grid;
           grid-template-columns:1fr 340px; gap:32px; }}
  @media(max-width:768px) {{ .main {{ grid-template-columns:1fr; padding:16px; }} }}

  /* Investor cards */
  .investor-card {{ background:var(--surface); border:1px solid var(--border); border-radius:16px;
                    margin-bottom:20px; overflow:hidden; transition:box-shadow .2s; }}
  .investor-card:hover {{ box-shadow:0 4px 24px rgba(0,0,0,0.4); }}
  .card-header {{ display:flex; justify-content:space-between; align-items:center;
                  padding:20px 24px; cursor:pointer; user-select:none; }}
  .card-title {{ display:flex; align-items:center; gap:16px; }}
  .card-avatar {{ font-size:32px; }}
  .card-name {{ font-size:18px; font-weight:700; }}
  .card-tagline {{ font-size:12px; color:var(--muted); margin-top:2px; font-style:italic; }}
  .signal-badge {{ color:white; font-weight:800; font-size:13px; padding:5px 14px;
                   border-radius:20px; letter-spacing:1px; }}
  .card-chevron {{ color:var(--muted); font-size:14px; transition:transform .2s; }}
  .card-chevron.open {{ transform:rotate(180deg); }}
  .card-body {{ padding:0 24px 24px; display:none; }}
  .card-body.open {{ display:block; }}
  .card-summary {{ background:var(--surface2); border-radius:10px; padding:16px;
                   font-size:14px; line-height:1.7; color:var(--text); margin-bottom:20px; }}
  .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:20px; }}
  @media(max-width:600px) {{ .two-col {{ grid-template-columns:1fr; }} }}
  .col-title {{ font-size:13px; font-weight:700; color:var(--muted); margin-bottom:10px; text-transform:uppercase; letter-spacing:.5px; }}
  .point-list {{ list-style:none; padding:0; }}
  .point-list li {{ font-size:13px; line-height:1.6; padding:6px 0;
                    border-bottom:1px solid rgba(71,85,105,0.4); color:var(--text); }}
  .point-list li:last-child {{ border-bottom:none; }}
  .progress-bar-wrap {{ display:flex; align-items:center; gap:12px; }}
  .progress-label {{ font-size:12px; color:var(--muted); white-space:nowrap; }}
  .progress-track {{ flex:1; background:var(--surface2); border-radius:99px; height:8px; overflow:hidden; }}
  .progress-fill {{ height:100%; border-radius:99px; transition:width .6s ease; }}
  .progress-pct {{ font-size:13px; font-weight:700; min-width:36px; text-align:right; }}

  /* Metrics table */
  .sidebar-card {{ background:var(--surface); border:1px solid var(--border); border-radius:16px;
                   overflow:hidden; position:sticky; top:24px; }}
  .sidebar-title {{ padding:16px 20px; font-weight:700; font-size:15px;
                    border-bottom:1px solid var(--border); background:var(--surface2); }}
  .metrics-table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  .metrics-table th {{ padding:10px 16px; text-align:left; color:var(--muted);
                        font-size:11px; text-transform:uppercase; letter-spacing:.5px;
                        background:var(--surface2); border-bottom:1px solid var(--border); }}
  .metrics-table td {{ padding:9px 16px; border-bottom:1px solid rgba(71,85,105,0.3); }}
  .metrics-table td:last-child {{ text-align:right; font-weight:600; font-variant-numeric:tabular-nums; }}
  .metrics-table tr:last-child td {{ border-bottom:none; }}
  .metric-good {{ color:var(--good) !important; }}
  .metric-mid {{ color:var(--mid) !important; }}
  .metric-bad {{ color:var(--bad) !important; }}
  .metric-na {{ color:var(--muted) !important; }}

  /* Company summary */
  .company-summary {{ background:var(--surface); border:1px solid var(--border); border-radius:16px;
                      padding:20px; margin-bottom:20px; font-size:14px; line-height:1.7;
                      color:var(--muted); max-height:120px; overflow:hidden;
                      position:relative; transition: max-height .3s; }}
  .company-summary.expanded {{ max-height:1000px; }}
  .expand-btn {{ background:none; border:none; color:var(--accent); cursor:pointer;
                 font-size:13px; padding:8px 0 0; display:block; }}

  /* Footer */
  footer {{ text-align:center; padding:32px; color:var(--muted); font-size:12px;
            border-top:1px solid var(--border); margin-top:32px; }}
</style>
</head>
<body>

<!-- Language toggle button -->
<div class="lang-toggle">
  <button class="lang-btn active" id="btn-zh" onclick="setLang('zh')">中文</button>
  <button class="lang-btn" id="btn-en" onclick="setLang('en')">EN</button>
</div>

<div class="hero">
  <div class="hero-inner">
    <div class="hero-top">
      <div>
        <div class="ticker-badge">{ticker}</div>
        <div class="company-name">{name}</div>
        <div class="company-meta">
          <span>📁 {d['sector']}</span>
          <span>🏭 {d['industry']}</span>
          {website_html}
          {employees_html}
        </div>
      </div>
      <div class="price-block">
        <div class="price-num">{price}</div>
        <div class="price-label" id="price-label">{d['currency']} · 实时报价</div>
      </div>
    </div>

    <div class="disclaimer" id="disclaimer">
      ⚠️ 本报告仅供教育和参考用途，不构成任何投资建议。所有分析均基于公开的财务数据，
      不代表巴菲特、芒格或段永平本人观点。投资有风险，决策需谨慎。
    </div>
    <div class="date-tag" id="date-tag">生成时间：{date_str} · 数据来源：Yahoo Finance (yfinance)</div>
  </div>
</div>

<div class="scorecard" style="max-width:1100px;margin:24px auto 0;padding:0 32px;">
  {scorecard_html}
</div>

<div class="main">
  <div class="left-col">
    <div class="company-summary" id="co-summary">
      {d['summary']}
    </div>
    <button class="expand-btn" id="expand-btn" onclick="toggleSummary()">展开更多 ▼</button>

    <div style="margin-top:24px;">
      {panels_html}
    </div>
  </div>

  <div class="right-col">
    <div class="sidebar-card">
      <div class="sidebar-title" id="sidebar-title">📊 关键财务指标</div>
      <table class="metrics-table">
        <thead><tr>
          <th id="metric-col-label">指标</th>
          <th id="metric-col-value">数值</th>
        </tr></thead>
        <tbody>
          {metrics_rows_html}
        </tbody>
      </table>
    </div>
  </div>
</div>

<footer id="footer">
  Stock Advisor Skill · JHU ISAI · Powered by yfinance + Python<br>
  <span id="footer-disclaimer">数据可能存在延迟，仅供参考，不构成投资建议。</span>
</footer>

<script>
  // ── Bilingual data injected from Python ──
  const ANALYSES = {js_data};

  let currentLang = 'zh';

  const UI = {{
    zh: {{
      priceLabel:      '{d['currency']} · 实时报价',
      disclaimer:      '⚠️ 本报告仅供教育和参考用途，不构成任何投资建议。所有分析均基于公开的财务数据，不代表巴菲特、芒格或段永平本人观点。投资有风险，决策需谨慎。',
      dateTag:         '生成时间：{date_str} · 数据来源：Yahoo Finance (yfinance)',
      expandMore:      '展开更多 ▼',
      collapse:        '收起 ▲',
      sidebarTitle:    '📊 关键财务指标',
      metricLabel:     '指标',
      metricValue:     '数值',
      footerNote:      '数据可能存在延迟，仅供参考，不构成投资建议。',
      prosTitle:       '✅ 优势因素',
      consTitle:       '⚠️ 风险因素',
      scoreLabel:      '综合评分',
      noPros:          '暂无明显优势',
      noCons:          '暂无明显风险',
    }},
    en: {{
      priceLabel:      '{d['currency']} · Live Quote',
      disclaimer:      '⚠️ This report is for educational purposes only and does not constitute investment advice. All analysis is based on public financial data and does not represent the views of Buffett, Munger, or Duan Yongping. Invest at your own risk.',
      dateTag:         'Generated: {date_str} · Data: Yahoo Finance (yfinance)',
      expandMore:      'Show More ▼',
      collapse:        'Collapse ▲',
      sidebarTitle:    '📊 Key Financial Metrics',
      metricLabel:     'Metric',
      metricValue:     'Value',
      footerNote:      'Data may be delayed. For reference only. Not investment advice.',
      prosTitle:       '✅ Strengths',
      consTitle:       '⚠️ Risk Factors',
      scoreLabel:      'Overall Score',
      noPros:          'No notable strengths',
      noCons:          'No notable risks',
    }}
  }};

  function setLang(lang) {{
    currentLang = lang;

    // Toggle button styles
    document.getElementById('btn-zh').classList.toggle('active', lang === 'zh');
    document.getElementById('btn-en').classList.toggle('active', lang === 'en');

    const t = UI[lang];

    // Static UI strings
    document.getElementById('price-label').textContent     = t.priceLabel;
    document.getElementById('disclaimer').textContent      = t.disclaimer;
    document.getElementById('date-tag').textContent        = t.dateTag;
    document.getElementById('sidebar-title').textContent   = t.sidebarTitle;
    document.getElementById('metric-col-label').textContent = t.metricLabel;
    document.getElementById('metric-col-value').textContent = t.metricValue;
    document.getElementById('footer-disclaimer').textContent = t.footerNote;

    // Expand button
    const expandBtn = document.getElementById('expand-btn');
    const summary = document.getElementById('co-summary');
    expandBtn.textContent = summary.classList.contains('expanded') ? t.collapse : t.expandMore;

    // Metric table label cells (use data-zh / data-en attributes)
    document.querySelectorAll('.metrics-table td span[data-zh]').forEach(el => {{
      el.textContent = el.getAttribute('data-' + lang);
    }});

    // Employees span (if present)
    document.querySelectorAll('[data-zh]').forEach(el => {{
      el.textContent = el.getAttribute('data-' + lang);
    }});

    // Per-investor card content
    ANALYSES.forEach((a, i) => {{
      document.getElementById('tagline-' + i).textContent  = '"' + a['tagline_' + lang] + '"';
      document.getElementById('summary-' + i).textContent  = a['summary_' + lang];
      document.getElementById('col-pros-title-' + i).textContent = t.prosTitle;
      document.getElementById('col-cons-title-' + i).textContent = t.consTitle;
      document.getElementById('score-label-' + i).textContent    = t.scoreLabel;

      const prosList = document.getElementById('pros-' + i);
      const consList = document.getElementById('cons-' + i);

      const points   = a['points_'   + lang];
      const warnings = a['warnings_' + lang];

      prosList.innerHTML = points.length
        ? points.map(p => '<li>' + p + '</li>').join('')
        : '<li style="color:#94a3b8">' + t.noPros + '</li>';

      consList.innerHTML = warnings.length
        ? warnings.map(w => '<li>' + w + '</li>').join('')
        : '<li style="color:#94a3b8">' + t.noCons + '</li>';
    }});
  }}

  function toggleCard(i) {{
    const body    = document.getElementById('body-' + i);
    const chevron = document.getElementById('chevron-' + i);
    body.classList.toggle('open');
    chevron.classList.toggle('open');
  }}

  function toggleSummary() {{
    const el  = document.getElementById('co-summary');
    const btn = document.getElementById('expand-btn');
    el.classList.toggle('expanded');
    const t = UI[currentLang];
    btn.textContent = el.classList.contains('expanded') ? t.collapse : t.expandMore;
  }}

  // Init: open first card, set default language
  document.addEventListener('DOMContentLoaded', () => {{
    toggleCard(0);
    setLang('zh');
  }});
</script>
</body>
</html>"""
    return html


# ─────────────────────────────────────────────
#  Entry Point
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_stock.py <TICKER>")
        print("Example: python analyze_stock.py AAPL")
        sys.exit(1)

    ticker = sys.argv[1].upper().strip()
    print(f"📡 正在获取 {ticker} 的财务数据...")

    try:
        data = fetch_data(ticker)
    except Exception as e:
        print(f"❌ 数据获取失败：{e}")
        sys.exit(1)

    if data["price"] is None:
        print(f"❌ 无法获取 {ticker} 的价格数据，请确认股票代码正确。")
        sys.exit(1)

    print(f"✅ 获取成功：{data['name']} (${data['price']:.2f})")
    print(f"📊 正在进行三维投资分析...")

    analyses = [
        analyze_buffett(data),
        analyze_munger(data),
        analyze_duan(data),
    ]

    for a in analyses:
        print(f"  {a['avatar']} {a['name']}: {a['signal']} ({a['score']}/{a['max_score']} pts)")

    print(f"🎨 正在生成 HTML 报告...")
    html = generate_html(data, analyses)

    output_file = f"{ticker}_report.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ 报告已生成：{output_file}")
    print(f"💡 用浏览器打开该文件即可查看交互式投资分析报告。")


if __name__ == "__main__":
    main()
