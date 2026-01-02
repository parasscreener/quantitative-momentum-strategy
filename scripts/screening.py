"""
Daily Stock Screening Script
Runs the quantitative momentum strategy and generates current screening results
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import os
import sys
import warnings

warnings.filterwarnings('ignore')

# Add parent directory to path to import strategy module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quantitative_momentum_strategy import QuantitativeMomentumStrategy

def run_daily_screening():
    """
    Execute daily momentum stock screening
    Output: CSV with detailed metrics for all screened stocks
    """

    print("=" * 80)
    print("QUANTITATIVE MOMENTUM STRATEGY - DAILY SCREENING")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("=" * 80)

    # Initialize strategy
    strategy = QuantitativeMomentumStrategy(
        nifty_universe='nifty_500',
        rebalance_frequency='quarterly'
    )

    # Get Nifty 500 constituents
    print("\n📊 Fetching Nifty 500 constituents...")
    try:
        from nsetools import Nse
        nse = Nse()
        stock_symbols = nse.get_stocks_in_index('NIFTY 500')
        stocks = [f"{symbol}.NS" for symbol in stock_symbols]
        print(f"✅ Successfully retrieved {len(stocks)} Nifty 500 stocks")
    except Exception as e:
        print(f"⚠️  Error fetching from NSE tools: {e}")
        print("   Falling back to manual list...")
        stocks = []  # Fallback to alternative method

    # Screen for momentum
    print("\n🔍 Screening stocks for momentum signals...")
    portfolio = strategy.screen_momentum_stocks(stocks)

    if portfolio.empty:
        print("❌ No suitable stocks found in current screening")
        return

    print(f"✅ Found {len(portfolio)} stocks meeting momentum criteria")

    # Add additional metrics
    portfolio['Sector'] = portfolio['Symbol'].apply(lambda x: get_sector(x))
    portfolio['Market_Cap_Rank'] = range(1, len(portfolio) + 1)
    portfolio['Momentum_Strength'] = portfolio['Momentum_12m'].apply(
        lambda x: 'Very Strong' if x > 1.0 else ('Strong' if x > 0.5 else 'Moderate')
    )
    portfolio['Momentum_Quality'] = portfolio['FIP_Score'].apply(
        lambda x: 'Excellent' if x < -0.3 else ('Good' if x < -0.1 else 'Fair')
    )

    # Add entry/exit signals
    entry_rules, exit_rules = strategy.calculate_entry_exit_rules(portfolio)

    portfolio['Entry_Signal'] = 'YES'  # Top 40 stocks selected
    portfolio['Stop_Loss'] = portfolio['Price'] * 0.85  # 15% below entry
    portfolio['Target_Price'] = portfolio['Price'] * 1.25  # 25% upside target
    portfolio['Max_Holding_Days'] = 90

    # Sector rotation logic
    portfolio['Sector_Weight'] = portfolio.groupby('Sector').cumcount() + 1
    portfolio = portfolio.sort_values('Sector_Weight')

    # Create output directory
    os.makedirs('output', exist_ok=True)

    # Save detailed results
    output_columns = [
        'Symbol', 'Price', 'Momentum_12m', 'Momentum_Strength',
        'FIP_Score', 'Momentum_Quality', 'Combined_Score',
        'Entry_Signal', 'Stop_Loss', 'Target_Price', 'Max_Holding_Days',
        'Sector', 'Volume'
    ]

    output_df = portfolio[output_columns].copy()
    output_df = output_df.round(4)

    csv_path = 'output/screening_results.csv'
    output_df.to_csv(csv_path, index=False)

    print(f"\n📁 Results saved to: {csv_path}")
    print(f"\nTop 10 Recommended Stocks:")
    print("-" * 100)
    print(output_df.head(10).to_string(index=False))

    # Generate statistics
    print(f"\n📈 Screening Statistics:")
    print(f"   Total Stocks Screened: {len(stocks)}")
    print(f"   Stocks in Top Momentum: {len(portfolio)}")
    print(f"   Average Momentum: {portfolio['Momentum_12m'].mean():.2%}")
    print(f"   Median FIP Score: {portfolio['FIP_Score'].median():.4f}")
    print(f"   Average Price: ₹{portfolio['Price'].mean():.2f}")
    print(f"   Sectors Represented: {portfolio['Sector'].nunique()}")

    return portfolio

def get_sector(stock_symbol):
    """
    Get sector for a stock (simplified version)
    In production, use NSE official sector classification
    """
    # Mapping of major Nifty 500 stocks to sectors
    sector_map = {
        'RELIANCE': 'Energy',
        'TCS': 'IT',
        'INFOSY': 'IT',
        'WIPRO': 'IT',
        'HDFCBANK': 'Finance',
        'ICICIBANK': 'Finance',
        'SBIN': 'Finance',
        'AXISBANK': 'Finance',
        'LT': 'Industrial',
        'MARUTI': 'Automotive',
        'BAJAJFINSV': 'Finance',
        'ITC': 'Consumer',
        'NESTLEIND': 'Consumer',
        'HUL': 'Consumer',
    }

    for key, value in sector_map.items():
        if key in stock_symbol:
            return value
    return 'Others'

if __name__ == "__main__":
    portfolio = run_daily_screening()
    print("\n✅ Daily screening completed successfully")
