"""
Generate HTML report from screening results
"""

import pandas as pd
from datetime import datetime
import os

def generate_html_report():
    """
    Create beautiful HTML report for email
    """

    csv_path = 'output/screening_results.csv'
    if not os.path.exists(csv_path):
        print("No screening results found")
        return

    df = pd.read_csv(csv_path)

    html_content = f"""
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
            h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .timestamp {{
                color: #ccc;
                font-size: 14px;
                margin-top: 10px;
            }}
            .summary {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-box {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #667eea;
            }}
            .stat-value {{
                font-size: 24px;
                font-weight: bold;
                color: #667eea;
            }}
            .stat-label {{
                font-size: 12px;
                color: #666;
                margin-top: 5px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            thead {{
                background-color: #f8f9fa;
                font-weight: bold;
                color: #333;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .positive {{
                color: #28a745;
                font-weight: bold;
            }}
            .negative {{
                color: #dc3545;
                font-weight: bold;
            }}
            .entry-yes {{
                background-color: #d4edda;
                color: #155724;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }}
            .rules {{
                background-color: #e7f3ff;
                border-left: 4px solid #2196F3;
                padding: 15px;
                margin: 20px 0;
                border-radius: 3px;
            }}
            .rules h3 {{
                margin-top: 0;
                color: #1976D2;
            }}
            .rules ul {{
                margin: 10px 0;
                padding-left: 20px;
            }}
            .rules li {{
                margin: 8px 0;
                font-size: 14px;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Quantitative Momentum Strategy</h1>
                <h2 style="margin: 10px 0; font-size: 18px;">Daily Stock Screening Report</h2>
                <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}</div>
            </div>

            <div class="summary">
                <div class="stat-box">
                    <div class="stat-value">{len(df)}</div>
                    <div class="stat-label">Stocks Selected</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{df['Momentum_12m'].mean():.1%}</div>
                    <div class="stat-label">Avg 12M Momentum</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">₹{df['Price'].mean():.0f}</div>
                    <div class="stat-label">Avg Entry Price</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{df['Sector'].nunique()}</div>
                    <div class="stat-label">Sectors Represented</div>
                </div>
            </div>

            <div class="rules">
                <h3>📋 Strategy Rules & Parameters</h3>
                <ul>
                    <li><strong>Momentum Lookback:</strong> 12 months (skip last month)</li>
                    <li><strong>Quality Filter:</strong> FIP (Frog-in-Pan) - prefer smooth momentum paths</li>
                    <li><strong>Portfolio Construction:</strong> 40 stocks, equal-weight</li>
                    <li><strong>Rebalance Frequency:</strong> Quarterly (Feb end, May end, Aug end, Nov end)</li>
                    <li><strong>Entry Rule:</strong> Combined momentum + quality score > threshold</li>
                    <li><strong>Exit Rule (Stop Loss):</strong> 15% below entry price</li>
                    <li><strong>Target Price:</strong> 25% above entry</li>
                    <li><strong>Max Holding Period:</strong> 90 days (quarterly rebalance)</li>
                </ul>
            </div>

            <h2 style="margin-top: 30px; color: #333;">Recommended Stocks for Today</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Symbol</th>
                        <th>Price (₹)</th>
                        <th>12M Momentum</th>
                        <th>Quality (FIP)</th>
                        <th>Entry Signal</th>
                        <th>Stop Loss (₹)</th>
                        <th>Target (₹)</th>
                        <th>Sector</th>
                    </tr>
                </thead>
                <tbody>
    """

    for idx, (_, row) in enumerate(df.head(20).iterrows(), 1):
        momentum_class = 'positive' if row['Momentum_12m'] > 0 else 'negative'
        entry_class = 'entry-yes' if row['Entry_Signal'] == 'YES' else ''

        html_content += f"""
                    <tr>
                        <td><strong>{idx}</strong></td>
                        <td><strong>{row['Symbol']}</strong></td>
                        <td>₹{row['Price']:.2f}</td>
                        <td class="{momentum_class}">{row['Momentum_12m']:.2%}</td>
                        <td>{row['Momentum_Quality']}</td>
                        <td><span class="{entry_class}">{row['Entry_Signal']}</span></td>
                        <td>₹{row['Stop_Loss']:.2f}</td>
                        <td>₹{row['Target_Price']:.2f}</td>
                        <td>{row['Sector']}</td>
                    </tr>
        """

    html_content += """
                </tbody>
            </table>

            <div class="rules" style="margin-top: 30px;">
                <h3>📊 Key Metrics Explained</h3>
                <ul>
                    <li><strong>Momentum (12M):</strong> 12-month cumulative return. Higher = stronger momentum</li>
                    <li><strong>Quality (FIP):</strong> % positive days - % negative days. Negative is better (smooth momentum)</li>
                    <li><strong>Stop Loss:</strong> 15% below entry price (risk management)</li>
                    <li><strong>Target:</strong> 25% above entry price (3:1 reward-to-risk ratio)</li>
                </ul>
            </div>

            <div class="rules" style="background-color: #fff3cd; border-left-color: #ffc107;">
                <h3>⚠️ Risk Disclaimer</h3>
                <ul>
                    <li>Momentum strategies are more volatile than passive investing</li>
                    <li>Drawdowns can be significant (20-30% during market corrections)</li>
                    <li>Discipline required to follow the algorithm during downturns</li>
                    <li>Past performance does not guarantee future results</li>
                </ul>
            </div>

            <div class="footer">
                <p>This report is generated automatically based on the Quantitative Momentum Strategy
                   as described in "Quantitative Momentum: A Practitioner's Guide" by Wesley R. Gray & Jack R. Vogel.</p>
                <p>Strategy Duration: 15+ year backtest performance</p>
                <p>Data Source: Yahoo Finance (via yfinance) | NSE Tools</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Save HTML
    html_path = 'output/report.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML report generated: {html_path}")

if __name__ == "__main__":
    generate_html_report()
