"""
Quarterly Portfolio Rebalance Execution
Manages position exits, entries, and portfolio transitions
"""

import pandas as pd
from datetime import datetime
import os

def execute_quarterly_rebalance():
    """
    Execute quarterly rebalance:
    1. Close all existing positions
    2. Screen for new momentum stocks
    3. Enter new 40-stock portfolio
    4. Calculate portfolio turnover
    """

    print("=" * 80)
    print("QUARTERLY REBALANCE EXECUTION")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("=" * 80)

    # Check if today is rebalance date
    today = datetime.now().date()
    rebalance_months = [2, 5, 8, 11]

    if today.month not in rebalance_months:
        print("❌ Not a scheduled rebalance date")
        return

    print(f"\n✅ Rebalance date: {today.strftime('%B %d, %Y')}")

    # Read previous portfolio (if exists)
    previous_portfolio_file = 'output/previous_portfolio.csv'
    new_portfolio_file = 'output/screening_results.csv'

    if not os.path.exists(new_portfolio_file):
        print("No new portfolio screening available")
        return

    # Load new screening results
    new_portfolio = pd.read_csv(new_portfolio_file)

    # Calculate turnover
    if os.path.exists(previous_portfolio_file):
        previous_portfolio = pd.read_csv(previous_portfolio_file)

        # Stocks removed
        removed = set(previous_portfolio['Symbol']) - set(new_portfolio['Symbol'])
        # Stocks added
        added = set(new_portfolio['Symbol']) - set(previous_portfolio['Symbol'])
        # Stocks continuing
        continuing = set(previous_portfolio['Symbol']) & set(new_portfolio['Symbol'])

        turnover_pct = (len(removed) / len(previous_portfolio)) * 100

        print(f"\n📊 PORTFOLIO TURNOVER:")
        print(f"   Stocks Removed: {len(removed)} ({turnover_pct:.1f}%)")
        print(f"   Stocks Added: {len(added)} ({(len(added)/len(new_portfolio))*100:.1f}%)")
        print(f"   Stocks Continuing: {len(continuing)}")
        print(f"   Total Portfolio Turnover: {turnover_pct:.1f}%")

        if removed:
            print(f"\n   Exiting Positions: {', '.join(list(removed)[:5])}...")
        if added:
            print(f"\n   Entering Positions: {', '.join(list(added)[:5])}...")

    # Calculate expected transaction costs
    rebalance_cost = 0.20  # 20 basis points per rebalance
    annual_cost = rebalance_cost * 4  # 4 rebalances per year

    print(f"\n💰 EXPECTED COSTS:")
    print(f"   Per Rebalance Cost: {rebalance_cost}%")
    print(f"   Annual Cost (4x rebalance): {annual_cost}%")

    # Save current portfolio as previous for next quarter
    new_portfolio.to_csv(previous_portfolio_file, index=False)

    # Generate rebalance report
    generate_rebalance_html(new_portfolio, len(removed) if os.path.exists(previous_portfolio_file) else 0)

    print(f"\n✅ Quarterly rebalance completed")
    print(f"   New portfolio saved")
    print(f"   Rebalance alert sent")

def generate_rebalance_html(portfolio, stocks_removed):
    """Generate HTML rebalance alert report"""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 8px;
            }}
            .alert {{
                background-color: #fff3cd;
                border: 2px solid #ffc107;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .alert h2 {{
                color: #856404;
                margin-top: 0;
            }}
            .checklist {{
                background-color: #e8f5e9;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .checklist li {{
                margin: 8px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f8f9fa;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Quarterly Rebalance Alert</h1>
            <p>Date: {datetime.now().strftime('%Y-%m-%d')}</p>

            <div class="alert">
                <h2>⚠️ Action Required: Portfolio Rebalance</h2>
                <p>The quarterly rebalancing period has arrived. Please review and execute the following actions:</p>
            </div>

            <div class="checklist">
                <h3>📋 Rebalance Execution Checklist:</h3>
                <ul>
                    <li>☐ Close all {stocks_removed} existing stock positions</li>
                    <li>☐ Record entry/exit prices and returns</li>
                    <li>☐ Calculate tax implications (long-term vs. short-term gains)</li>
                    <li>☐ Review new 40-stock portfolio recommendations</li>
                    <li>☐ Open new positions in recommended stocks</li>
                    <li>☐ Set new stop-loss levels (15% below entry)</li>
                    <li>☐ Set target prices (25% above entry)</li>
                    <li>☐ Update portfolio tracking spreadsheet</li>
                    <li>☐ Review sector allocation across portfolio</li>
                    <li>☐ Document all trades for tax records</li>
                </ul>
            </div>

            <h2>New Portfolio ({len(portfolio)} Stocks)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Symbol</th>
                        <th>Price (₹)</th>
                        <th>12M Momentum</th>
                        <th>FIP Score</th>
                    </tr>
                </thead>
                <tbody>
    """

    for idx, (_, row) in enumerate(portfolio.head(20).iterrows(), 1):
        html += f"""
                    <tr>
                        <td>{idx}</td>
                        <td><strong>{row['Symbol']}</strong></td>
                        <td>₹{row['Price']:.2f}</td>
                        <td>{row['Momentum_12m']:.2%}</td>
                        <td>{row['FIP_Score']:.4f}</td>
                    </tr>
        """

    html += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    os.makedirs('output', exist_ok=True)
    with open('output/rebalance_alert.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("✅ Rebalance HTML alert generated")

if __name__ == "__main__":
    execute_quarterly_rebalance()
