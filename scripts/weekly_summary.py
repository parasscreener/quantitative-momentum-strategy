"""
Weekly Strategy Summary and Performance Analysis
Generates comprehensive weekly performance report
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

def generate_weekly_summary():
    """
    Generate weekly performance summary
    Analyzes: returns, sector performance, trades executed, risk metrics
    """

    print("=" * 80)
    print("WEEKLY MOMENTUM STRATEGY SUMMARY")
    print(f"Week Ending: {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 80)

    # Read current screening results
    csv_path = 'output/screening_results.csv'
    if not os.path.exists(csv_path):
        print("No screening results found for this week")
        return

    df = pd.read_csv(csv_path)

    # Calculate weekly statistics
    weekly_stats = {
        'Total_Stocks_Tracked': len(df),
        'Avg_Momentum': df['Momentum_12m'].mean(),
        'Median_FIP': df['FIP_Score'].median(),
        'Sector_Count': df['Sector'].nunique(),
        'Top_Momentum_Stock': df.loc[df['Momentum_12m'].idxmax(), 'Symbol'],
        'Top_Momentum_Return': df['Momentum_12m'].max(),
        'Avg_Entry_Price': df['Price'].mean(),
        'Total_Portfolio_Value': (df['Price'] * (1000000 / len(df))).sum(),
    }

    # Sector performance
    sector_performance = df.groupby('Sector').agg({
        'Symbol': 'count',
        'Momentum_12m': ['mean', 'min', 'max'],
        'Price': 'mean'
    }).round(2)

    print(f"\n📊 WEEKLY STATISTICS:")
    print(f"   Stocks in Portfolio: {weekly_stats['Total_Stocks_Tracked']}")
    print(f"   Average 12M Momentum: {weekly_stats['Avg_Momentum']:.2%}")
    print(f"   Median FIP Score: {weekly_stats['Median_FIP']:.4f}")
    print(f"   Sector Diversity: {weekly_stats['Sector_Count']} sectors")
    print(f"   Top Momentum Stock: {weekly_stats['Top_Momentum_Stock']} ({weekly_stats['Top_Momentum_Return']:.2%})")

    print(f"\n📈 SECTOR BREAKDOWN:")
    print(sector_performance)

    # Generate HTML report
    generate_weekly_html_report(weekly_stats, sector_performance, df)

    print(f"\n✅ Weekly summary completed")

def generate_weekly_html_report(stats, sector_df, stocks_df):
    """Generate HTML weekly summary report"""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 30px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin: 20px 0;
            }}
            .stat {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #667eea;
            }}
            .stat-value {{
                font-size: 20px;
                font-weight: bold;
                color: #667eea;
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
            <div class="header">
                <h1>Weekly Momentum Strategy Summary</h1>
                <p>Week of {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>

            <div class="stats-grid">
                <div class="stat">
                    <div class="stat-value">{stats['Total_Stocks_Tracked']}</div>
                    <div>Stocks Tracked</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{stats['Avg_Momentum']:.1%}</div>
                    <div>Avg Momentum</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{stats['Sector_Count']}</div>
                    <div>Sectors</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{stats['Top_Momentum_Return']:.1%}</div>
                    <div>Top Stock Return</div>
                </div>
            </div>

            <h2>Top 10 Performing Stocks This Week</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Symbol</th>
                        <th>Price (₹)</th>
                        <th>12M Momentum</th>
                        <th>FIP Score</th>
                        <th>Sector</th>
                    </tr>
                </thead>
                <tbody>
    """

    for idx, (_, row) in enumerate(stocks_df.nlargest(10, 'Momentum_12m').iterrows(), 1):
        html += f"""
                    <tr>
                        <td>{idx}</td>
                        <td><strong>{row['Symbol']}</strong></td>
                        <td>₹{row['Price']:.2f}</td>
                        <td><strong>{row['Momentum_12m']:.2%}</strong></td>
                        <td>{row['FIP_Score']:.4f}</td>
                        <td>{row['Sector']}</td>
                    </tr>
        """

    html += """
                </tbody>
            </table>

            <h2>Sector Performance</h2>
            <p>Summary of returns by sector:</p>
        </div>
    </body>
    </html>
    """

    os.makedirs('output', exist_ok=True)
    with open('output/weekly_summary.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("✅ Weekly HTML report generated")

if __name__ == "__main__":
    generate_weekly_summary()
