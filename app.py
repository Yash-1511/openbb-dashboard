import streamlit as st
from openbb import obb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
from dotenv import load_dotenv
import os
import io
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from PIL import Image

load_dotenv()

# set environment variable
obb.user.credentials.fmp_api_key = os.getenv("FMP_API_KEY")
st.set_page_config(page_title="OpenBB Financial Dashboard", layout="wide")

# Add OpenBB Dashboard Header and Description
st.sidebar.image(
    "https://avatars.githubusercontent.com/u/80064875?s=280&v=4", width=100
)  # You'll need to download and add the OpenBB logo
st.sidebar.markdown(
    """
# OpenBB Financial Dashboard
"""
)

# Add Documentation/Help Section
if st.sidebar.checkbox("Show Documentation"):
    st.sidebar.markdown(
        """
    ### How to Use This Dashboard
    1. Enter a stock ticker in the sidebar
    2. Select date range for analysis
    3. Choose technical indicators
    4. Explore fundamental data
    5. Simulate portfolio performance
    
    ### Features
    - Real-time stock data
    - Technical analysis tools
    - Fundamental analysis
    - Portfolio optimization
    - Risk metrics
    """
    )
# Sidebar Inputs
st.sidebar.title("User Inputs")

# Stock ticker input
ticker = st.sidebar.text_input("Enter Stock Ticker", value="AAPL").upper()

# Date range selection
start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())


@st.cache_data
def fetch_stock_data(ticker, start_date, end_date):
    data = obb.equity.price.historical(
        symbol=ticker,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
    ).to_dataframe()
    return data


try:
    stock_data = fetch_stock_data(ticker, start_date, end_date)
except Exception as e:
    st.error(f"Error fetching data: {e}")
    print(f"Error fetching data: {e}")
    st.stop()

st.title(f"Stock Analysis for {ticker}")
st.subheader("Closing Price Chart")

fig_price = px.line(
    stock_data,
    x=stock_data.index,
    y="close",
    labels={"close": "Price", "index": "Date"},
)
st.plotly_chart(fig_price, use_container_width=True)

# Save the chart to an image for export
with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
    fig_price.write_image(temp.name)
    price_chart_path = temp.name

# Technical Analysis
st.sidebar.subheader("Technical Indicators")
ma_periods = st.sidebar.multiselect(
    "Select Moving Averages", [5, 10, 20, 50, 100, 200], default=[20, 50]
)

for period in ma_periods:
    stock_data[f"MA_{period}"] = stock_data["close"].rolling(window=period).mean()

st.subheader("Price with Moving Averages")
fig_ma = go.Figure()
fig_ma.add_trace(
    go.Scatter(x=stock_data.index, y=stock_data["close"], name="Close Price")
)

for period in ma_periods:
    fig_ma.add_trace(
        go.Scatter(
            x=stock_data.index, y=stock_data[f"MA_{period}"], name=f"MA {period}"
        )
    )

st.plotly_chart(fig_ma, use_container_width=True)

# Save the chart to an image for export
with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
    fig_ma.write_image(temp.name)
    ma_chart_path = temp.name


# Bollinger Bands
def calculate_bollinger_bands(data, window=20):
    data["MA"] = data["close"].rolling(window=window).mean()
    data["STD"] = data["close"].rolling(window=window).std()
    data["Upper"] = data["MA"] + (data["STD"] * 2)
    data["Lower"] = data["MA"] - (data["STD"] * 2)
    return data


stock_data = calculate_bollinger_bands(stock_data)

st.subheader("Bollinger Bands")
fig_bb = go.Figure()
fig_bb.add_trace(
    go.Scatter(
        x=stock_data.index,
        y=stock_data["Upper"],
        name="Upper Band",
        line=dict(color="rgba(173,216,230,0.2)"),
    )
)
fig_bb.add_trace(
    go.Scatter(
        x=stock_data.index,
        y=stock_data["Lower"],
        name="Lower Band",
        fill="tonexty",
        fillcolor="rgba(173,216,230,0.2)",
        line=dict(color="rgba(173,216,230,0.2)"),
    )
)
fig_bb.add_trace(
    go.Scatter(
        x=stock_data.index,
        y=stock_data["close"],
        name="Close Price",
        line=dict(color="blue"),
    )
)

st.plotly_chart(fig_bb, use_container_width=True)

# Save the chart to an image for export
with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
    fig_bb.write_image(temp.name)
    bb_chart_path = temp.name


# RSI
def calculate_rsi(data, periods=14):
    delta = data["close"].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.ewm(com=(periods - 1), min_periods=periods).mean()
    avg_loss = loss.ewm(com=(periods - 1), min_periods=periods).mean()
    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))
    return data


stock_data = calculate_rsi(stock_data)

st.subheader("Relative Strength Index (RSI)")
fig_rsi = px.line(
    stock_data, x=stock_data.index, y="RSI", labels={"index": "Date", "RSI": "RSI"}
)
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
st.plotly_chart(fig_rsi, use_container_width=True)

# Save the chart to an image for export
with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
    fig_rsi.write_image(temp.name)
    rsi_chart_path = temp.name

# Add Market Overview Section
st.header("Market Overview")
market_overview_option = st.selectbox(
    "Select Market Data",
    ["Market Index Performance", "Sector Performance", "Market Fear & Greed"],
)


@st.cache_data
def fetch_market_data():
    try:
        if market_overview_option == "Market Index Performance":
            indices = ["SPY", "QQQ", "DIA"]
            market_data = pd.DataFrame()
            for index in indices:
                data = obb.equity.price.historical(
                    symbol=index, start_date=start_date.strftime("%Y-%m-%d")
                ).to_dataframe()
                market_data[index] = data["close"]
            return market_data
        elif market_overview_option == "Sector Performance":
            return obb.economy.overview(interval="1d").to_dataframe()
    except Exception as e:
        st.error(f"Error fetching market data: {e}")
        return None


market_data = fetch_market_data()
if market_data is not None:
    st.plotly_chart(px.line(market_data), use_container_width=True)

# Save the chart to an image for export
with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
    px.line(market_data).write_image(temp.name)
    market_chart_path = temp.name

# Fundamental Analysis
st.header("Fundamental Analysis")

# Select statement type
statement_type = st.selectbox(
    "Select Financial Statement", ["Income Statement", "Balance Sheet", "Cash Flow"]
)


@st.cache_data
def fetch_financial_statement(ticker, statement_type):
    if statement_type == "Income Statement":
        data = obb.equity.fundamental.income(
            symbol=ticker, provider="fmp"
        ).to_dataframe()
    elif statement_type == "Balance Sheet":
        data = obb.equity.fundamental.balance(
            symbol=ticker, provider="fmp"
        ).to_dataframe()
    elif statement_type == "Cash Flow":
        data = obb.equity.fundamental.cash(symbol=ticker, provider="fmp").to_dataframe()
    return data


try:
    financial_data = fetch_financial_statement(ticker, statement_type)
    st.subheader(f"{statement_type} for {ticker}")
    st.dataframe(financial_data)
except Exception as e:
    st.error(f"Error fetching financial statements: {e}")

st.subheader("Key Financial Ratios")


@st.cache_data
def fetch_financial_ratios(ticker):
    data = obb.equity.fundamental.ratios(symbol=ticker).to_dataframe()
    return data


try:
    ratios_data = fetch_financial_ratios(ticker)
    st.dataframe(ratios_data)
except Exception as e:
    st.error(f"Error fetching financial ratios: {e}")

# Portfolio Simulation
st.header("Portfolio Simulation")

st.sidebar.subheader("Portfolio Inputs")

# User inputs
portfolio_tickers = st.sidebar.text_input(
    "Enter Tickers (separated by commas)", value="AAPL,MSFT,GOOGL"
)
weights_input = st.sidebar.text_input(
    "Enter Weights (comma-separated)", value="0.4,0.3,0.3"
)

# Process inputs
tickers = [t.strip().upper() for t in portfolio_tickers.split(",")]
weights = [float(w) for w in weights_input.split(",")]

if len(tickers) != len(weights):
    st.error("Number of tickers and weights must match.")
    st.stop()
elif sum(weights) != 1:
    st.error("Weights must sum up to 1.")
    st.stop()

@st.cache_data
def fetch_portfolio_data(tickers, start_date, end_date):
    portfolio_data = pd.DataFrame()
    for ticker in tickers:
        data = obb.equity.price.historical(
            symbol=ticker,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        ).to_dataframe()
        portfolio_data[ticker] = data["close"]
    return portfolio_data

portfolio_data = fetch_portfolio_data(tickers, start_date, end_date)

# Calculate daily returns
returns = portfolio_data.pct_change().dropna()

# Calculate portfolio returns
portfolio_returns = returns.dot(weights)

# Calculate cumulative returns
cumulative_returns = (1 + portfolio_returns).cumprod()

st.subheader("Portfolio Cumulative Returns")
fig_portfolio = px.line(cumulative_returns, labels={"index": "Date", "value": "Cumulative Returns"})
st.plotly_chart(fig_portfolio, use_container_width=True)

st.subheader("Portfolio Risk Metrics")

# # Calculate metrics
volatility = portfolio_returns.std() * (252 ** 0.5)
annual_return = portfolio_returns.mean() * 252
sharpe_ratio = annual_return / volatility

st.write(f"Annualized Return: {annual_return:.2%}")
st.write(f"Annualized Volatility: {volatility:.2%}")
st.write(f"Sharpe Ratio: {sharpe_ratio:.2f}")


# Add Risk Analysis Section
st.header("Advanced Risk Analysis")
if st.checkbox("Show Value at Risk (VaR) Analysis"):
    confidence_level = st.slider("Confidence Level", 0.9, 0.99, 0.95)
    returns = stock_data["close"].pct_change().dropna()
    var = returns.quantile(1 - confidence_level)
    st.write(f"Value at Risk ({confidence_level*100}%): {var:.2%}")


if st.sidebar.button("Export Analysis to PDF"):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "Stock Analysis Report")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 70, f"Date: {pd.Timestamp.today().strftime('%Y-%m-%d')}")

    # Adding Price Chart
    p.drawString(100, height - 100, "Closing Price Chart:")
    price_chart_image = Image.open(price_chart_path)
    p.drawImage(ImageReader(price_chart_image), 100, height - 400, width=400, height=250)
    
    # Adding Moving Averages Chart
    p.drawString(100, height - 430, "Price with Moving Averages:")
    ma_chart_image = Image.open(ma_chart_path)
    p.drawImage(ImageReader(ma_chart_image), 100, height - 730, width=400, height=250)
    
    # New page for Bollinger Bands
    p.showPage()
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "Bollinger Bands Analysis")
    
    # Adding Bollinger Bands Chart
    bb_chart_image = Image.open(bb_chart_path)
    p.drawImage(ImageReader(bb_chart_image), 100, height - 400, width=400, height=250)
    
    # New page for RSI
    p.showPage()
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "Relative Strength Index (RSI) Analysis")
    
    # Adding RSI Chart
    rsi_chart_image = Image.open(rsi_chart_path)
    p.drawImage(ImageReader(rsi_chart_image), 100, height - 400, width=400, height=250)
    
    # Finalize PDF
    p.showPage()
    p.save()

    buffer.seek(0)
    st.sidebar.download_button(
        label="Download PDF Report",
        data=buffer,
        file_name="stock_analysis_report.pdf",
        mime="application/pdf"
    )


# Add Feedback Section
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
### Feedback
Help us improve! [Submit Feedback](https://github.com/Yash-1511/openbb-dashboard/issues)
"""
)

# Add Footer
st.markdown("---")
st.markdown(
    """
<div style='text-align: center'>
    <p>Built with ❤️ using OpenBB SDK | Created for Hacktoberfest 2024</p>
    <p>View source code on <a href="https://github.com/Yash-1511/openbb-dashboard">GitHub</a></p>
</div>
""",
    unsafe_allow_html=True,
)
