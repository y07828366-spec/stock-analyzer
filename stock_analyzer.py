# coding: utf-8
import gradio as gr
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体（兼容Linux/Windows/Mac）
import platform
system = platform.system()
if system == 'Windows':
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
elif system == 'Darwin':
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC']
else:
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def get_symbol_seed(symbol):
    """根据股票代码生成确定性种子，保证同一代码每次生成的模拟数据一致"""
    return sum(ord(c) * (i + 1) for i, c in enumerate(symbol)) % 2**31


def generate_simulated_data(symbol, start_date, end_date):
    """生成模拟数据 - 根据用户选择的日期范围动态生成"""
    seed = get_symbol_seed(symbol)
    rng = np.random.RandomState(seed)

    # 解析日期
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    # 生成指定日期范围的工作日序列
    dates = pd.bdate_range(start=start, end=end)
    days = len(dates)

    # 至少生成30天数据防止出错
    if days < 30:
        days = 30
        dates = pd.bdate_range(end=end, periods=days)

    # 根据股票代码生成不同的波动率和趋势特征
    drift = rng.uniform(-0.0002, 0.001)
    volatility = rng.uniform(0.01, 0.03)
    returns = rng.normal(drift, volatility, days)
    prices = 100 * np.exp(np.cumsum(returns))

    df = pd.DataFrame({
        'Date': dates,
        'Close': prices,
        'Open': prices * (1 + rng.normal(0, 0.005, days)),
        'High': prices * (1 + rng.uniform(0.005, 0.02, days)),
        'Low': prices * (1 - rng.uniform(0.005, 0.02, days)),
        'Volume': rng.randint(1000000, 50000000, days),
        'Symbol': symbol
    })

    # 确保 High >= Close >= Low
    df['High'] = df[['High', 'Close', 'Open']].max(axis=1)
    df['Low'] = df[['Low', 'Close', 'Open']].min(axis=1)

    return df


def get_dividend_analysis(ticker, symbol):
    """获取股息分析数据"""
    try:
        div = ticker.dividends
        if div.empty:
            return {
                '年化股息': 0.0,
                '股息率%': 0.0,
                '股息次数': 0,
                '最近股息': 0.0
            }

        # 最近一年的股息
        one_year_ago = pd.Timestamp.now() - pd.Timedelta(days=365)
        recent_div = div[div.index > one_year_ago]
        annual_div = float(recent_div.sum()) if not recent_div.empty else float(div.iloc[-4:].sum())

        # 获取当前价格计算股息率
        info = ticker.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        if current_price == 0:
            hist = ticker.history(period="5d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else 100

        div_yield = (annual_div / current_price) * 100 if current_price > 0 else 0

        return {
            '年化股息': round(annual_div, 4),
            '股息率%': round(div_yield, 2),
            '股息次数': len(recent_div) if not recent_div.empty else len(div.iloc[-12:]),
            '最近股息': round(float(div.iloc[-1]), 4) if not div.empty else 0.0
        }
    except Exception:
        return {
            '年化股息': 0.0,
            '股息率%': 0.0,
            '股息次数': 0,
            '最近股息': 0.0
        }


def calculate_momentum_indicators(stock_df):
    """计算涨跌/动量指标"""
    stock_df = stock_df.sort_values('Date').copy()
    closes = stock_df['Close'].values

    # 日涨跌幅
    daily_returns = np.diff(closes) / closes[:-1]

    # 波动率 (年化)
    volatility = float(np.std(daily_returns) * np.sqrt(252) * 100)

    # 最大回撤
    cummax = np.maximum.accumulate(closes)
    drawdowns = (closes - cummax) / cummax
    max_drawdown = float(np.min(drawdowns) * 100)

    # 20日/60日均线
    if len(closes) >= 20:
        ma20 = float(np.mean(closes[-20:]))
        price_vs_ma20 = ((closes[-1] - ma20) / ma20) * 100
    else:
        ma20 = closes[-1]
        price_vs_ma20 = 0.0

    if len(closes) >= 60:
        ma60 = float(np.mean(closes[-60:]))
        price_vs_ma60 = ((closes[-1] - ma60) / ma60) * 100
    else:
        ma60 = closes[-1]
        price_vs_ma60 = 0.0

    # 近1月/3月/6月/1年涨跌幅
    def period_return(days):
        if len(closes) > days:
            return ((closes[-1] - closes[-(days+1)]) / closes[-(days+1)]) * 100
        return 0.0

    return {
        '波动率%': round(volatility, 2),
        '最大回撤%': round(max_drawdown, 2),
        '距20日均线%': round(price_vs_ma20, 2),
        '距60日均线%': round(price_vs_ma60, 2),
        '近1月%': round(period_return(21), 2),
        '近3月%': round(period_return(63), 2),
        '近6月%': round(period_return(126), 2),
        '近1年%': round(period_return(252), 2),
    }


def analyze_stocks(stock_input, start_date, end_date, data_source):
    """分析股票数据 - 修复版"""
    symbols = [s.strip().upper() for s in stock_input.replace('，', ',').split(',') if s.strip()]

    if not symbols:
        return "请输入股票代码", None, None, None, None

    # 获取数据
    all_data = []
    ticker_objects = {}

    if data_source == "Yahoo Finance (实时)":
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                ticker_objects[symbol] = ticker
                df = ticker.history(start=start_date, end=end_date, progress=False)
                if not df.empty and len(df) >= 2:
                    df['Symbol'] = symbol
                    df.reset_index(inplace=True)
                    all_data.append(df)
            except Exception as e:
                continue

        if not all_data:
            return "从 Yahoo Finance 获取数据失败，请检查股票代码或切换至模拟数据", None, None, None, None
    else:
        for symbol in symbols:
            df = generate_simulated_data(symbol, start_date, end_date)
            all_data.append(df)

    df = pd.concat(all_data, ignore_index=True)

    # 主分析结果
    results = []
    # 涨跌/动量分析
    momentum_results = []
    # 股息分析
    dividend_results = []

    for symbol in df['Symbol'].unique():
        stock_df = df[df['Symbol'] == symbol].sort_values('Date')
        if len(stock_df) < 2:
            continue

        start_p = float(stock_df['Close'].iloc[0])
        end_p = float(stock_df['Close'].iloc[-1])
        total_ret = ((end_p - start_p) / start_p) * 100

        # 年化计算
        start_d = pd.to_datetime(stock_df['Date'].iloc[0])
        end_d = pd.to_datetime(stock_df['Date'].iloc[-1])
        years = (end_d - start_d).days / 365.25
        annual_ret = (((end_p / start_p) ** (1/years)) - 1) * 100 if years > 0 else 0

        results.append({
            '股票': symbol,
            '起始价': round(start_p, 2),
            '最新价': round(end_p, 2),
            '总收益率%': round(total_ret, 2),
            '年化收益率%': round(annual_ret, 2),
            '数据天数': len(stock_df)
        })

        # 涨跌/动量指标
        momentum = calculate_momentum_indicators(stock_df)
        momentum['股票'] = symbol
        momentum_results.append(momentum)

        # 股息分析 (仅在Yahoo Finance模式下)
        if data_source == "Yahoo Finance (实时)" and symbol in ticker_objects:
            div_data = get_dividend_analysis(ticker_objects[symbol], symbol)
        else:
            # 模拟股息数据
            div_data = {
                '年化股息': round(get_symbol_seed(symbol) % 500 / 100, 2),
                '股息率%': round((get_symbol_seed(symbol) % 50) / 10, 2),
                '股息次数': get_symbol_seed(symbol) % 4 + 1,
                '最近股息': round(get_symbol_seed(symbol) % 100 / 100, 2)
            }
        div_data['股票'] = symbol
        dividend_results.append(div_data)

    if not results:
        return "分析失败，无有效数据", None, None, None, None

    result_df = pd.DataFrame(results)
    momentum_df = pd.DataFrame(momentum_results)
    dividend_df = pd.DataFrame(dividend_results)

    # ===== 生成图表 =====
    n_stocks = len(result_df)
    fig = plt.figure(figsize=(16, 10 + n_stocks * 1.5))
    gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

    # 1. 总收益率对比柱状图
    ax1 = fig.add_subplot(gs[0, 0])
    colors = ['#27ae60' if x > 0 else '#e74c3c' for x in result_df['总收益率%']]
    bars = ax1.bar(result_df['股票'], result_df['总收益率%'], color=colors, edgecolor='white', linewidth=0.5)
    ax1.set_title('总收益率对比 (%)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('收益率 (%)')
    ax1.tick_params(axis='x', rotation=30)
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax1.grid(True, alpha=0.3, axis='y')
    # 添加数值标签
    for bar, val in zip(bars, result_df['总收益率%']):
        ax1.text(bar.get_x() + bar.get_width()/2., val,
                f'{val:.1f}%', ha='center', va='bottom' if val > 0 else 'top', fontsize=9)

    # 2. 价格走势 (归一化)
    ax2 = fig.add_subplot(gs[0, 1])
    for symbol in df['Symbol'].unique():
        data = df[df['Symbol'] == symbol].sort_values('Date')
        if len(data) > 0:
            normalized = data['Close'] / data['Close'].iloc[0] * 100
            ax2.plot(data['Date'], normalized, label=symbol, linewidth=2, alpha=0.85)
    ax2.set_title('价格走势 (归一化 = 100)', fontsize=13, fontweight='bold')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylabel('相对价格')

    # 3. 各期涨跌幅对比
    ax3 = fig.add_subplot(gs[1, 0])
    x = np.arange(n_stocks)
    width = 0.2
    periods = ['近1月%', '近3月%', '近6月%', '近1年%']
    colors_period = ['#3498db', '#9b59b6', '#f39c12', '#e67e22']
    for i, (period, color) in enumerate(zip(periods, colors_period)):
        values = momentum_df[period].values
        offset = (i - 1.5) * width
        bars = ax3.bar(x + offset, values, width, label=period, color=color, alpha=0.85)
    ax3.set_xticks(x)
    ax3.set_xticklabels(momentum_df['股票'], rotation=30)
    ax3.set_title('各期涨跌幅对比 (%)', fontsize=13, fontweight='bold')
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3, axis='y')

    # 4. 波动率与最大回撤
    ax4 = fig.add_subplot(gs[1, 1])
    x = np.arange(n_stocks)
    width = 0.35
    bars1 = ax4.bar(x - width/2, momentum_df['波动率%'], width, label='波动率%', color='#3498db', alpha=0.85)
    bars2 = ax4.bar(x + width/2, momentum_df['最大回撤%'].abs(), width, label='最大回撤% (绝对值)', color='#e74c3c', alpha=0.85)
    ax4.set_xticks(x)
    ax4.set_xticklabels(momentum_df['股票'], rotation=30)
    ax4.set_title('波动率 vs 最大回撤', fontsize=13, fontweight='bold')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3, axis='y')

    # 5. 股息分析
    ax5 = fig.add_subplot(gs[2, 0])
    colors_div = ['#27ae60' if x > 0 else '#95a5a6' for x in dividend_df['股息率%']]
    bars = ax5.bar(dividend_df['股票'], dividend_df['股息率%'], color=colors_div, edgecolor='white', linewidth=0.5)
    ax5.set_title('股息率对比 (%)', fontsize=13, fontweight='bold')
    ax5.set_ylabel('股息率 (%)')
    ax5.tick_params(axis='x', rotation=30)
    ax5.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, dividend_df['股息率%']):
        if val > 0:
            ax5.text(bar.get_x() + bar.get_width()/2., val,
                    f'{val:.2f}%', ha='center', va='bottom', fontsize=9)

    # 6. 均线系统偏离度
    ax6 = fig.add_subplot(gs[2, 1])
    colors_ma20 = ['#27ae60' if x > 0 else '#e74c3c' for x in momentum_df['距20日均线%']]
    colors_ma60 = ['#2980b9' if x > 0 else '#e67e22' for x in momentum_df['距60日均线%']]

    x = np.arange(n_stocks)
    width = 0.35
    ax6.bar(x - width/2, momentum_df['距20日均线%'], width, label='距20日均线%', color=colors_ma20, alpha=0.85)
    ax6.bar(x + width/2, momentum_df['距60日均线%'], width, label='距60日均线%', color=colors_ma60, alpha=0.85)
    ax6.set_xticks(x)
    ax6.set_xticklabels(momentum_df['股票'], rotation=30)
    ax6.set_title('均线偏离度 (%)', fontsize=13, fontweight='bold')
    ax6.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax6.legend(fontsize=9)
    ax6.grid(True, alpha=0.3, axis='y')

    # 汇总信息
    summary = f"分析完成: {n_stocks} 只股票\n"
    summary += f"平均年化收益率: {result_df['年化收益率%'].mean():.2f}%\n"
    best = result_df.loc[result_df['年化收益率%'].idxmax()]
    summary += f"最佳表现: {best['股票']} (年化 {best['年化收益率%']:.2f}%)\n"
    avg_div_yield = dividend_df['股息率%'].mean()
    summary += f"平均股息率: {avg_div_yield:.2f}%"

    return summary, result_df, momentum_df, dividend_df, fig


# ===== Gradio 界面 =====
with gr.Blocks(title="股票数据分析系统 v2.0", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 股票数据可视化分析系统 v2.0")
    gr.Markdown("支持实时 Yahoo Finance 数据或本地模拟数据 | 新增涨跌分析 & 股息分析")

    with gr.Row():
        with gr.Column(scale=1):
            stock_input = gr.Textbox(
                label="股票代码",
                value="AAPL,MSFT,TSLA,NVDA,GOOGL,AMZN,META,JPM,KO,WMT",
                placeholder="逗号分隔，如: AAPL,MSFT,TSLA,NVDA,GOOGL,AMZN,META,JPM,KO,WMT"
            )

            start_date = gr.Textbox(
                label="开始日期",
                value="2022-01-01",
                placeholder="格式: YYYY-MM-DD"
            )

            end_date = gr.Textbox(
                label="结束日期",
                value=datetime.now().strftime("%Y-%m-%d"),
                placeholder="格式: YYYY-MM-DD"
            )

            data_source = gr.Dropdown(
                choices=["Yahoo Finance (实时)", "模拟数据 (免联网)"],
                value="模拟数据 (免联网)",
                label="数据源"
            )

            analyze_btn = gr.Button("开始分析", variant="primary", size="lg")

            gr.Markdown("""
            **使用说明：**
            - 美股代码: AAPL, MSFT, TSLA, NVDA, JPM, KO 等
            - A股代码: 000001.SZ, 600519.SS 等
            - 日期格式: YYYY-MM-DD
            - 如 Yahoo 限流，请切换"模拟数据"模式
            """)

        with gr.Column(scale=2):
            summary = gr.Textbox(label="分析摘要", lines=4, interactive=False)

            with gr.Tabs():
                with gr.TabItem("收益率概览"):
                    data_table = gr.DataFrame(label="收益率数据")

                with gr.TabItem("涨跌分析"):
                    momentum_table = gr.DataFrame(label="动量指标")

                with gr.TabItem("股息分析"):
                    dividend_table = gr.DataFrame(label="股息数据")

            chart = gr.Plot(label="可视化图表")

    # 事件绑定
    analyze_btn.click(
        fn=analyze_stocks,
        inputs=[stock_input, start_date, end_date, data_source],
        outputs=[summary, data_table, momentum_table, dividend_table, chart]
    )

    # 示例
    gr.Examples(
        examples=[
            ["AAPL,MSFT,GOOGL", "2020-01-01", "2024-12-31", "模拟数据 (免联网)"],
            ["TSLA,NVDA,META", "2022-01-01", "2024-12-31", "模拟数据 (免联网)"],
            ["JPM,BAC,KO,PEP", "2021-01-01", "2024-12-31", "模拟数据 (免联网)"],
            ["AAPL", "2023-01-01", "2024-12-31", "Yahoo Finance (实时)"],
        ],
        inputs=[stock_input, start_date, end_date, data_source],
        label="快速示例 (点击自动填充)"
    )

if __name__ == "__main__":
    print("=" * 50)
    print("  股票数据分析系统 v2.0 启动中...")
    print("=" * 50)
    print("请等待浏览器窗口打开")
    print("或手动访问: http://localhost:7860")
    print("-" * 50)
    demo.launch(share=True)
