# ACC102 Mini Assignment - Reflection

## What I Built and Why

For Track 4 (Interactive Tool), I built a **Stock Data Visualisation & Analysis System** that allows users to compare multiple stocks across return, risk, momentum, and dividend dimensions through a web browser. The core motivation was to solve a real problem: retail investors and students lack access to affordable, easy-to-use multi-stock comparison tools. Professional platforms like Bloomberg Terminal cost thousands of dollars, while free alternatives often require coding knowledge. My tool bridges this gap with a clean Gradio interface that generates comprehensive visual analysis in seconds.

## The Development Process

I started by defining the data pipeline: collection (Yahoo Finance API), transformation (cleaning and validation), analysis (return/risk/momentum/dividend metrics), and visualisation (6-panel Matplotlib dashboard). The most challenging part was designing the analysis engine to compute meaningful financial metrics accurately - particularly annualised volatility, maximum drawdown, and moving average deviations. I spent significant time validating formulas against established finance textbooks to ensure correctness.

The interactive web interface was built with Gradio because it allows rapid deployment with a single `launch(share=True)` call, generating a public link accessible to anyone. This was critical for Track 4's marker-access requirement. I also implemented a deterministic simulation mode using hash-based random seeds, so the tool remains fully functional even when Yahoo Finance rate-limits API access.

## Key Technical Decisions

1. **Gradio over Streamlit**: While Streamlit offers more layout flexibility, Gradio's `share=True` feature provides instant public links without external deployment services - ideal for a coursework deadline.

2. **Deterministic simulation**: Each ticker symbol maps to a unique random seed via hash function. This means "AAPL" always generates the same synthetic data, making results reproducible and demo-friendly.

3. **6-panel visualisation**: Instead of one crowded chart, I separated comparisons into 6 focused panels (returns, trends, multi-period, risk, dividends, momentum), following Edward Tufte's principle of maximizing data-ink ratio.

4. **Real data from Yahoo Finance**: The database contains 7,530 actual trading-day observations across 10 stocks (AAPL, MSFT, TSLA, NVDA, GOOGL, AMZN, META, JPM, KO, WMT from 2022-2024), not synthetic data, giving the analysis real-world credibility and demonstrating the tool's ability to handle multiple securities simultaneously.

## Limitations I Acknowledge

- Yahoo Finance API has rate limits; the tool may need re-launching if blocked
- Gradio public links expire after ~72 hours of inactivity
- The tool does not support real-time intraday data (daily only)
- Portfolio-level metrics (correlation, beta, Sharpe ratio) are not yet implemented
- The UI is functional but not as polished as a commercial product

## What I Would Improve Next

- Add a local SQLite cache layer to reduce API dependency
- Implement portfolio analytics (correlation matrix, efficient frontier)
- Migrate to Streamlit for better visual design control
- Add support for A-shares and cryptocurrency markets

## AI Disclosure

I used AI tools (specifically Kimi AI) during this assignment for the following purposes:
- **Code structure guidance**: understanding how to organise the Gradio interface and Matplotlib subplots
- **Debugging assistance**: fixing the date-range bug in the simulation mode (the original code hardcoded 5 years regardless of user input)
- **Documentation**: formatting the README and this reflection to meet academic standards

I verified all financial formulas independently against standard finance references (Bodie, Kane & Marcus: *Investments*). All data comes from Yahoo Finance, and all analysis results were manually spot-checked for reasonableness. The core analytical logic, design decisions, and interpretation of findings are my own work.

---

*Word count: ~580 words*
