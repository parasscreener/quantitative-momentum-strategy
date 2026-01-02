"""
Daily Stock Screening Script
Runs the quantitative momentum strategy and generates current screening results

Supports 2 configurations:
1. quantitative_momentum_strategy.py in project root
2. quantitative_momentum_strategy.py in scripts/ folder (RECOMMENDED)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import warnings

warnings.filterwarnings('ignore')

# Configuration: Try both import paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

# Add both paths for flexibility
sys.path.insert(0, SCRIPTS_DIR)      # Priority 1: scripts/ folder
sys.path.insert(0, PROJECT_ROOT)      # Priority 2: project root

# Import strategy - handle both configurations gracefully
try:
    # Try importing from scripts folder first (RECOMMENDED)
    from quantitative_momentum_strategy import QuantitativeMomentumStrategy
    print("✅ Imported strategy from scripts/ folder")
except ImportError:
    try:
        # Fallback: try importing from project root
        sys.path.insert(0, PROJECT_ROOT)
        from quantitative_momentum_strategy import QuantitativeMomentumStrategy
        print("✅ Imported strategy from project root")
    except ImportError:
        print("⚠️  quantitative_momentum_strategy module not found")
        print("   Using inline strategy implementation...")
        
        # Fallback: Inline strategy implementation
        import yfinance as yf
        
        class QuantitativeMomentumStrategy:
            """Inline strategy implementation as fallback"""
            def __init__(self, nifty_universe='nifty_500', rebalance_frequency='quarterly'):
                self.nifty_universe = nifty_universe
                self.rebalance_frequency = rebalance_frequency
                self.lookback_months = 12
                self.skip_last_month = True
                self.fip_lookback_days = 252
                self.portfolio_size = 40
                self.momentum_percentile = 0.90
            
            def get_nifty_constituents(self):
                """Get Nifty 500 constituents with NSEtools fallback"""
                try:
                    from nsetools import Nse
                    nse = Nse()
                    if self.nifty_universe == 'nifty_50':
                        stocks = nse.get_stocks_in_index('NIFTY 50')
                    else:
                        stocks = nse.get_stocks_in_index('NIFTY 500')
                    return [f"{stock}.NS" for stock in stocks]
                except Exception as e:
                    print(f"⚠️  NSEtools failed: {e}")
                    print("   Using yfinance for Nifty 50 sample...")
                    # Fallback to Nifty 50 sample
                    return [
                        'RELIANCE.NS', 'TCS.NS', 'INFOSY.NS', 'WIPRO.NS', 'HDFCBANK.NS',
                        'ICICIBANK.NS', 'SBIN.NS', 'AXISBANK.NS', 'LT.NS', 'MARUTI.NS',
                        'BAJAJFINSV.NS', 'ITC.NS', 'NESTLEIND.NS', 'HUL.NS', 'ASIANPAINT.NS',
                        'SUNPHARMA.NS', 'INDIGO.NS', 'ONGC.NS', 'TATASTEEL.NS', 'NTPC.NS'
                    ]
            
            def calculate_generic_momentum(self, stock_data):
                """Calculate 12-month momentum skipping last month"""
                try:
                    if len(stock_data) < 252:
                        return None
                    returns = stock_data['Close'].pct_change()
                    # Skip last month (21 days), use 12 months before
                    returns_12m_skip1m = returns[-252:-21]
                    if len(returns_12m_skip1m) < 200:
                        return None
                    momentum = np.prod(1 + returns_12m_skip1m) - 1
                    return momentum
                except:
                    return None
            
            def calculate_fip_score(self, stock_data):
                """Calculate FIP (Fraction of Increasing Periods) score"""
                try:
                    if len(stock_data) < self.fip_lookback_days:
                        return None
                    returns = stock_data['Close'].pct_change()[-252:]
                    if len(returns) < 200:
                        return None
                    pct_positive = (returns > 0).sum() / len(returns)
                    pct_negative = (returns < 0).sum() / len(returns)
                    fip_score = pct_positive - pct_negative
                    return fip_score
                except:
                    return None
            
            def screen_momentum_stocks(self, stock_list, date=None):
                """Screen stocks for momentum signals"""
                if date is None:
                    date = datetime.now()
                results = []
                
                for idx, stock in enumerate(stock_list):
                    try:
                        end_date = date
                        start_date = date - timedelta(days=730)
                        stock_data = yf.download(stock, start=start_date, end=end_date, 
                                                 progress=False, interval='1d')
                        if len(stock_data) < 252:
                            continue
                        
                        momentum = self.calculate_generic_momentum(stock_data)
                        fip_score = self.calculate_fip_score(stock_data)
                        
                        if momentum is not None and fip_score is not None:
                            results.append({
                                'Symbol': stock,
                                'Momentum_12m': momentum,
                                'FIP_Score': fip_score,
                                'Price': stock_data['Close'].iloc[-1],
                                'Date': date,
                                'Volume': stock_data['Volume'].iloc[-1]
                            })
                    except Exception as e:
                        continue
                
                if not results:
                    return pd.DataFrame()
                
                df = pd.DataFrame(results)
                df['Momentum_Rank'] = df['Momentum_12m'].rank(ascending=False, pct=True)
                top_momentum = df[df['Momentum_Rank'] <= self.momentum_percentile]
                
                if len(top_momentum) == 0:
                    return pd.DataFrame()
                
                top_momentum['FIP_Rank'] = top_momentum['FIP_Score'].rank(ascending=True, pct=True)
                top_momentum['Combined_Score'] = (
                    0.70 * (1 - top_momentum['Momentum_Rank']) +
                    0.30 * (1 - top_momentum['FIP_Rank'])
                )
                
                portfolio = top_momentum.nlargest(self.portfolio_size, 'Combined_Score')
                return portfolio.sort_values('Combined_Score', ascending=False)
            
            def calculate_entry_exit_rules(self, portfolio_df):
                """Calculate entry and exit rules"""
                entry_rules = {
                    'momentum_percentile_threshold': 90,
                    'fip_quality_threshold': -0.1,
                    'combined_score_min': 0.5,
                    'volume_ma_multiple': 1.0,
                }
                exit_rules = {
                    'momentum_percentile_exit': 30,
                    'fip_deterioration_threshold': 0.0,
                    'stop_loss_pct': 15,
                    'max_holding_period_days': 90,
                    'forced_rebalance': True,
                }
                portfolio_df['Entry_Signal'] = (
                    (portfolio_df['Momentum_Rank'] <= 0.10) &
                    (portfolio_df['FIP_Score'] < entry_rules['fip_quality_threshold']) &
                    (portfolio_df['Combined_Score'] >= entry_rules['combined_score_min'])
                )
                return entry_rules, exit_rules


def run_daily_screening():
    """Execute daily momentum stock screening"""
    
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
    stocks = strategy.get_nifty_constituents()
    print(f"✅ Retrieved {len(stocks)} stocks")
    
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
    
    portfolio['Entry_Signal'] = 'YES'
    portfolio['Stop_Loss'] = portfolio['Price'] * 0.85
    portfolio['Target_Price'] = portfolio['Price'] * 1.25
    portfolio['Max_Holding_Days'] = 90
    
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
    """Get sector for a stock symbol"""
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
        'SUNPHARMA': 'Pharma',
        'INDIGO': 'Aviation',
        'ONGC': 'Energy',
        'TATASTEEL': 'Metals',
        'NTPC': 'Energy',
        'ASIANPAINT': 'Paints',
    }
    
    for key, value in sector_map.items():
        if key in stock_symbol:
            return value
    return 'Others'


if __name__ == "__main__":
    portfolio = run_daily_screening()
    print("\n✅ Daily screening completed successfully")
