# OpenBB Financial Dashboard

## Overview

This project is a Streamlit-based financial dashboard that leverages the OpenBB SDK to provide comprehensive stock analysis, portfolio simulation, and financial data visualization. The dashboard offers the following features:

- Stock price analysis with interactive charts
- Technical indicators including Moving Averages, Bollinger Bands, and RSI
- Fundamental analysis with financial statements and key ratios
- Portfolio simulation with cumulative returns and risk metrics
- Multiple data provider options

## Prerequisites

- Python 3.11+
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Yash-1511/openbb-dashboard.git
   cd openbb-dashboard
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Setting Up Environment Variables

1. Create a `.env` file in the project root directory.

2. Add your Financial Modeling Prep (FMP) API key to the `.env` file:
   ```
   FMP_API_KEY=your_fmp_api_key_here
   ```

   You can obtain an API key by signing up at [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs/).

## Running the Application

1. Ensure you're in the project directory and your virtual environment is activated (if you're using one).

2. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

3. Open your web browser and go to `http://localhost:8501` to view the dashboard.

## Using the Dashboard

1. **Stock Analysis**:
   - Enter a stock ticker in the sidebar.
   - Select a date range for analysis.
   - Choose a data provider from the available options.

2. **Technical Analysis**:
   - View the closing price chart.
   - Select moving average periods to display on the chart.
   - Analyze Bollinger Bands and RSI indicators.

3. **Fundamental Analysis**:
   - Select a financial statement type (Income Statement, Balance Sheet, or Cash Flow).
   - View key financial ratios for the selected stock.

4. **Portfolio Simulation**:
   - Enter multiple stock tickers separated by commas.
   - Specify the weight for each stock in the portfolio.
   - View cumulative returns and risk metrics for the simulated portfolio.


Ensure you have the necessary API keys for the data provider you wish to use.

## Contributing

Contributions to improve the dashboard are welcome. Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature.
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your fork.
5. Submit a pull request with a clear description of your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenBB SDK](https://github.com/OpenBB-finance/OpenBBTerminal) for providing the financial data and analysis tools.
- [Streamlit](https://streamlit.io/) for the web application framework.
- All the open-source libraries used in this project.

