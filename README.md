# Stock Data Visualisation & Analysis System

**ACC102 Mini Assignment - Track 4: Interactive Tool**

---

## 1. Problem & User

Individual investors and students often struggle to compare multiple stocks across different dimensions (returns, risk, momentum, dividends) without expensive professional software. This interactive tool allows users to input any stock tickers, select a date range, and instantly receive a multi-dimensional visual analysis - making equity comparison accessible to anyone with a browser.

**Target user**: retail investors, finance students, or anyone who wants quick, visual stock comparisons without coding knowledge.

## 2. Data

| Item | Detail |
|------|--------|
| **Source** | Yahoo Finance (via yfinance API) |
| **Access date** | 18 April 2025 |
| **URL** | https://finance.yahoo.com |
| **Stocks in database** | **10** - AAPL, MSFT, TSLA, NVDA, GOOGL, AMZN, META, JPM, KO, WMT |
| **Time range** | 2022-01-03 to 2024-12-31 (3 years) |
| **Key fields** | Date, Symbol, Open, High, Low, Close, Volume, Dividends |
| **Total records** | **7,530** trading-day observations |
| **Database tables** | 7 (stock_data, daily_indicators, monthly_returns, yearly_summary, analysis_results, momentum_indicators, dividend_data) |

**Alternative data source**: built-in simulation mode generates deterministic synthetic data for any ticker when Yahoo Finance is rate-limited or offline.

## 3. Methods

The project follows a **data pipeline**: collection -> transformation -> analysis -> visualisation.

**Step 1 - Data Collection** (`yfinance` API or simulated data generator)
- Fetches OHLCV + dividend data for user-specified tickers and date range
- Simulation mode uses a deterministic seed derived from the ticker symbol to ensure reproducibility
- Supports **unlimited number of stocks** - the tool loops through all user-provided tickers

**Step 2 - Data Transformation**
- Validates and cleans price data (ensures High >= Close >= Low integrity)
- Filters data to the user-selected date range
- Calculates daily returns series for each stock

**Step 3 - Analysis Engine**
- **Return metrics**: total return, annualised return (CAGR)
- **Risk metrics**: annualised volatility (std * sqrt(252)), maximum drawdown
- **Momentum indicators**: distance from 20-day and 60-day moving averages
- **Period returns**: 1-month, 3-month, 6-month, 1-year rolling returns
- **Dividend analysis**: annual dividend, dividend yield, payout frequency, most recent dividend

**Step 4 - Visualisation**
- 6-panel Matplotlib figure: return comparison bar chart, normalised price trend, multi-period return comparison, volatility vs drawdown scatter, dividend yield comparison, moving average deviation
- Handles **any number of stocks** - each stock gets its own line/bar in the charts

**Step 5 - Web Interface**
- Gradio Blocks UI with tabbed output (returns / momentum / dividends / charts)
- Public link generation via `share=True` for marker access

## 4. Key Findings (10-Stock Analysis)

| Stock | Total Return | Annual Return | Volatility | Max Drawdown | Div Yield |
|-------|-------------|---------------|------------|--------------|-----------|
| **NVDA** | **+490.29%** | **+94.40%** | 51.18% | -66.42% | 0.03% |
| **META** | **+163.30%** | **+41.57%** | 39.79% | -76.00% | 0.00% |
| **AAPL** | **+39.84%** | **+11.86%** | 27.08% | -30.91% | 1.14% |
| **AMZN** | **+39.45%** | **+11.75%** | 35.61% | -56.16% | 0.00% |
| **JPM** | **+36.76%** | **+11.01%** | 25.97% | -34.63% | 2.71% |
| **MSFT** | **+29.18%** | **+8.93%** | 27.56% | -35.58% | 2.01% |
| **GOOGL** | **+28.21%** | **+8.66%** | 31.69% | -45.00% | 0.00% |
| **WMT** | **+12.58%** | **+4.01%** | 21.87% | -20.21% | 1.51% |
| **KO** | **+7.94%** | **+2.58%** | 18.40% | -15.47% | 3.30% |
| **TSLA** | **+0.98%** | **+0.33%** | 61.26% | -72.97% | 0.00% |

- **NVDA dominates** with nearly 5x total return, driven by AI chip demand - but carries high volatility (51%) and a -66% max drawdown
- **META recovered spectacularly** after its 2022 crash (-76% drawdown), delivering 163% total return
- **JPM offers the best dividend yield** (2.71%) among profitable growth stocks, combining income with 36% capital appreciation
- **KO is the safest bet** - lowest volatility (18.4%) and smallest drawdown (-15.5%), with the highest dividend yield (3.30%)
- **TSLA is the most volatile** stock (61% volatility) with extreme drawdown (-73%), barely breaking even over 3 years

## 5. How to Run

### Prerequisites
- Python 3.12 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Launch the Application

```bash
python stock_analyzer.py
```

After launch, the terminal displays:

```
Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://xxxx.gradio.live
```

- **Local access**: open http://127.0.0.1:7860 in your browser
- **Public link**: share the `https://xxxx.gradio.live` URL (accessible to the marker)

### Analysing Multiple Stocks

Enter comma-separated ticker symbols in the input box:

```
AAPL,MSFT,TSLA,NVDA,GOOGL,AMZN,META,JPM,KO,WMT
```

The tool handles **any number of stocks** - from 1 to 20+ (limited only by Yahoo Finance API rate limits in real-time mode).

### Alternative: Simulated Data Mode
If Yahoo Finance is rate-limited, select **"Simulated Data (免联网)"** from the dropdown. The tool generates deterministic synthetic data for your selected tickers and date range without requiring an internet connection.

## 6. Product Link / Demo

- **Interactive tool**: [Gradio public link generated on launch] (see Section 5)
- **Demo video**: [1-3 minute screen recording showing tool usage with 10 stocks]
- **Database**: `data/stock_database.xlsx` - complete dataset with 7 analysis tables (15,470 rows)

## 7. Limitations & Next Steps

**Current limitations:**
- Yahoo Finance API has rate limits; heavy usage may trigger temporary blocks
- Gradio public links expire after ~72 hours of inactivity (re-launching generates a new link)
- Simulated data is synthetic and should not be used for actual investment decisions
- Limited to daily-level data; intraday analysis is not supported

**Planned improvements:**
- Add a local SQLite cache to reduce API calls and enable offline historical lookup
- Extend to support A-shares (SSE/SZSE) and cryptocurrency tickers
- Add portfolio-level analytics (correlation matrix, Sharpe ratio, beta)
- Migrate from Gradio to Streamlit for more flexible layout control
- Implement user authentication to save analysis history

---

## Repository Structure

```
.
|-- stock_analyzer.py        # Main application (Gradio + analysis engine)
|-- notebook.ipynb           # Jupyter notebook: data -> cleaning -> analysis -> output
|-- README.md                # This file
|-- reflection.md            # Reflection + AI disclosure
|-- requirements.txt         # Python dependencies
|-- data/
|   |-- stock_database.xlsx  # Complete database (7 tables, 15,470 rows, 10 stocks)
|-- figures/
|   |-- [charts exported from notebook]
```

## Data Source Citation

| Data Content | Source Name | Source URL |
|-------------|-------------|------------|
| Historical prices (all 10 stocks) | Yahoo Finance | https://finance.yahoo.com |
| AAPL | Yahoo Finance | https://finance.yahoo.com/quote/AAPL/history |
| MSFT | Yahoo Finance | https://finance.yahoo.com/quote/MSFT/history |
| TSLA | Yahoo Finance | https://finance.yahoo.com/quote/TSLA/history |
| NVDA | Yahoo Finance | https://finance.yahoo.com/quote/NVDA/history |
| GOOGL | Yahoo Finance | https://finance.yahoo.com/quote/GOOGL/history |
| AMZN | Yahoo Finance | https://finance.yahoo.com/quote/AMZN/history |
| META | Yahoo Finance | https://finance.yahoo.com/quote/META/history |
| JPM | Yahoo Finance | https://finance.yahoo.com/quote/JPM/history |
| KO | Yahoo Finance | https://finance.yahoo.com/quote/KO/history |
| WMT | Yahoo Finance | https://finance.yahoo.com/quote/WMT/history |

---

*Built for ACC102 Mini Assignment - Track 4: Interactive Tool (+20 bonus)*
