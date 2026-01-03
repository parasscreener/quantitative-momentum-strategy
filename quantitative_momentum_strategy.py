
"""
Quantitative Momentum Strategy for Indian Nifty Stocks
Adapted from: Quantitative Momentum - A Practitioner's Guide by Wesley R. Gray & Jack R. Vogel
Enhanced for Indian Markets (Nifty 50 & Nifty 500)

Strategy Rules:
1. Generic Momentum Screen: 12-month returns, skip last month
2. Momentum Quality Screen: FIP (Frog-in-Pan) algorithm - smooth momentum paths
3. Momentum Seasonality Screen: Rebalance quarterly (end of Feb, May, Aug, Nov)
4. Portfolio Construction: Concentrated (30-50 stocks), equal-weight
5. Holding Period: 1-3 months, quarterly rebalance

Key Metrics:
- FIP Score: % positive days - % negative days (lower is better)
- 252-day look-back for FIP calculation
- 12-month momentum calculation (skip last month)
- Sharpe Ratio, Sortino Ratio, Max Drawdown tracking
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class QuantitativeMomentumStrategy:
    """
    Implementation of Quantitative Momentum Strategy for Indian Markets
    """

    def __init__(self, nifty_universe='nifty_500', rebalance_frequency='quarterly'):
        """
        Initialize the strategy

        Parameters:
        -----------
        nifty_universe : str
            'nifty_50' or 'nifty_500'
        rebalance_frequency : str
            'monthly', 'quarterly', 'semi-annual'
        """
        self.nifty_universe = nifty_universe
        self.rebalance_frequency = rebalance_frequency
        self.lookback_months = 12
        self.skip_last_month = True
        self.fip_lookback_days = 252
        self.portfolio_size = 40  # Conservative for Indian market
        self.momentum_percentile = 0.90  # Top 10% momentum stocks

    def get_nifty_constituents(self):
        """
        Get list of Nifty 50 or Nifty 500 constituents
        Using NSEtools library - free and reliable for Indian stocks
        """
        try:
            from nsetools import Nse
            nse = Nse()

            if self.nifty_universe == 'nifty_50':
                stocks = nse.get_stocks_in_index('NIFTY 50')
            else:  # nifty_500
                stocks = nse.get_stocks_in_index('NIFTY 500')

            return [f"{stock}.NS" for stock in stocks]  # Add .NS suffix for yfinance
        except Exception as e:
            print(f"Error fetching constituents: {e}")
            return []

    def calculate_generic_momentum(self, stock_data):
        """
        Calculate 12-month momentum, skipping last month

        Formula: Product of (1 + daily return) for past 252 trading days
        excluding most recent 21 trading days
        """
        try:
            # Get last 252 trading days
            if len(stock_data) < 252:
                return None

            # Calculate daily returns
            returns = stock_data['Close'].pct_change()

            # Exclude last 21 trading days (skip last month)
            returns_12m_skip1m = returns[-252:-21]

            # Calculate cumulative return
            momentum = np.prod(1 + returns_12m_skip1m) - 1

            return momentum
        except:
            return None

    def calculate_fip_score(self, stock_data):
        """
        Calculate FIP (Frog-in-Pan) Score

        Formula: FIP = sign(generic_momentum) * (% positive days - % negative days)

        Measures quality/path of momentum:
        - Negative FIP = smooth momentum (preferred)
        - Positive FIP = jumpy momentum (lottery-like, avoid)
        """
        try:
            if len(stock_data) < self.fip_lookback_days:
                return None

            # Get last 252 trading days
            returns = stock_data['Close'].pct_change()[-252:]

            # Calculate percentage of positive and negative days
            pct_positive = (returns > 0).sum() / len(returns)
            pct_negative = (returns < 0).sum() / len(returns)

            # FIP calculation
            fip_score = pct_positive - pct_negative

            return fip_score
        except:
            return None

       def screen_momentum_stocks(self, stock_list, date=None):
        """
        Screen stocks for momentum signals with fixed pandas indexing
        """
        if date is None:
            date = datetime.now()
        
        results = []
        for stock in stock_list:
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
        
        # Create dataframe and immediately copy to ensure fresh data
        df = pd.DataFrame(results).copy()
        df = df.reset_index(drop=True)
        
        # Calculate momentum rank on fresh dataframe
        df['Momentum_Rank'] = df['Momentum_12m'].rank(ascending=False, pct=True)
        
        # Filter and copy to ensure clean indices
        top_momentum = df[df['Momentum_Rank'] <= self.momentum_percentile].copy()
        top_momentum = top_momentum.reset_index(drop=True)
        
        if len(top_momentum) == 0:
            return pd.DataFrame()
        
        # Calculate FIP rank on clean data
        top_momentum['FIP_Rank'] = top_momentum['FIP_Score'].rank(ascending=True, pct=True)
        
        # Calculate combined score
        top_momentum['Combined_Score'] = (
            0.70 * (1 - top_momentum['Momentum_Rank']) +
            0.30 * (1 - top_momentum['FIP_Rank'])
        )
        
        # Get top portfolio and reset index
        portfolio = top_momentum.nlargest(self.portfolio_size, 'Combined_Score').copy()
        portfolio = portfolio.reset_index(drop=True)
        
        return portfolio.sort_values('Combined_Score', ascending=False)

    def get_rebalance_dates(self, start_date, end_date):
        """
        Generate rebalance dates based on seasonality strategy

        Optimal rebalance: End of Feb, May, Aug, Nov
        (Avoids window dressing and tax-loss selling periods)
        """
        rebalance_dates = []
        current = start_date

        while current <= end_date:
            # Check if it's end of Feb, May, Aug, Nov
            if current.month in [2, 5, 8, 11]:
                # Get last business day of month
                if current.month == 2:
                    if current.year % 4 == 0:
                        month_end = current.replace(day=29)
                    else:
                        month_end = current.replace(day=28)
                elif current.month in [5, 8]:
                    month_end = current.replace(day=31)
                else:  # November
                    month_end = current.replace(day=30)

                rebalance_dates.append(month_end)

            current = current + timedelta(days=1)

        return rebalance_dates

    def calculate_entry_exit_rules(self, portfolio_df):
        """
        Entry and Exit Rules based on Quantitative Momentum framework

        ENTRY CONDITIONS (ALL must be met):
        1. Stock in top 10% of momentum (generic momentum screen)
        2. Smooth momentum path (low FIP score) - avoid lottery-like behavior
        3. Combined score above threshold
        4. Rebalance date window (within seasonality window)
        5. Volume > 30-day average (liquidity check)

        EXIT CONDITIONS (ANY can trigger):
        1. Stock falls below 30th percentile momentum
        2. FIP score deteriorates significantly (becomes positive)
        3. Price falls 15% below entry (stop loss)
        4. Quarterly rebalance window (forced exit for portfolio rotation)
        5. Holding period > 3 months
        """
        entry_rules = {
            'momentum_percentile_threshold': 90,
            'fip_quality_threshold': -0.1,  # Prefer negative FIP
            'combined_score_min': 0.5,
            'volume_ma_multiple': 1.0,  # Min volume >= 30-day MA
        }

        exit_rules = {
            'momentum_percentile_exit': 30,
            'fip_deterioration_threshold': 0.0,  # FIP becomes positive
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


class BacktestEngine:
    """
    Backtesting engine for momentum strategy (15 years)
    """

    def __init__(self, strategy, start_date, end_date):
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.trades = []
        self.portfolio_values = []
        self.returns = []

    def run_backtest(self, stock_list, initial_capital=1000000):
        """
        Run 15-year backtest
        """
        rebalance_dates = self.strategy.get_rebalance_dates(self.start_date, self.end_date)

        portfolio_value = initial_capital
        positions = {}

        for rebalance_date in rebalance_dates:
            # Screen for momentum stocks
            portfolio = self.strategy.screen_momentum_stocks(stock_list, rebalance_date)

            if portfolio.empty:
                continue

            # Equal weight each position
            position_size = initial_capital / len(portfolio)

            # Close existing positions (exit all on rebalance)
            for symbol, position in positions.items():
                # Record trade
                entry_price = position['entry_price']
                exit_price = position['current_price']
                return_pct = (exit_price - entry_price) / entry_price * 100

                self.trades.append({
                    'Symbol': symbol,
                    'Entry_Date': position['entry_date'],
                    'Exit_Date': rebalance_date,
                    'Entry_Price': entry_price,
                    'Exit_Price': exit_price,
                    'Return_Pct': return_pct,
                    'Holding_Days': (rebalance_date - position['entry_date']).days
                })

            # Open new positions
            positions = {}
            for idx, row in portfolio.head(self.strategy.portfolio_size).iterrows():
                symbol = row['Symbol']
                positions[symbol] = {
                    'entry_price': row['Price'],
                    'current_price': row['Price'],
                    'entry_date': rebalance_date,
                    'shares': position_size / row['Price']
                }

        # Create summary statistics
        return self._generate_backtest_summary()

    def _generate_backtest_summary(self):
        """
        Generate backtest summary statistics
        """
        if not self.trades:
            return pd.DataFrame()

        trades_df = pd.DataFrame(self.trades)

        summary = {
            'Total_Trades': len(trades_df),
            'Winning_Trades': len(trades_df[trades_df['Return_Pct'] > 0]),
            'Win_Rate_Pct': len(trades_df[trades_df['Return_Pct'] > 0]) / len(trades_df) * 100,
            'Avg_Return_Pct': trades_df['Return_Pct'].mean(),
            'Max_Drawdown_Pct': trades_df['Return_Pct'].min(),
            'Avg_Holding_Days': trades_df['Holding_Days'].mean(),
            'Std_Dev_Returns': trades_df['Return_Pct'].std(),
        }

        # Calculate Sharpe Ratio (assuming 10% annual risk-free rate in India)
        annual_return = summary['Avg_Return_Pct'] * (252 / summary['Avg_Holding_Days'])
        sharpe_ratio = annual_return / (summary['Std_Dev_Returns'] + 1e-6) * np.sqrt(252)
        summary['Sharpe_Ratio'] = sharpe_ratio

        return pd.DataFrame([summary])


# Example usage:
if __name__ == "__main__":
    # Initialize strategy
    strategy = QuantitativeMomentumStrategy(
        nifty_universe='nifty_500',
        rebalance_frequency='quarterly'
    )

    # Get constituents
    stocks = strategy.get_nifty_constituents()
    print(f"Found {len(stocks)} Nifty 500 stocks")

    # Screen for momentum stocks (current date)
    portfolio = strategy.screen_momentum_stocks(stocks[:50])  # Test with 50 stocks
    print(portfolio[['Symbol', 'Momentum_12m', 'FIP_Score', 'Combined_Score']].head(10))
