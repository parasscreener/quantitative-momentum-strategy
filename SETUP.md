# Quantitative Momentum Strategy Setup Guide
## For Indian Nifty 50 & Nifty 500 Stocks

---

## 📋 Table of Contents
1. Project Overview
2. Prerequisites
3. Local Setup
4. GitHub Actions Configuration
5. Deployment
6. Strategy Parameters
7. Monitoring & Troubleshooting

---

## 🎯 Project Overview

This is a complete implementation of the **Quantitative Momentum Strategy** adapted for Indian markets, based on "Quantitative Momentum: A Practitioner's Guide" by Wesley R. Gray & Jack R. Vogel.

### Key Features:
- **Daily Automated Screening**: Identifies momentum stocks at 9:30 AM IST (Monday-Friday)
- **15-Year Backtesting**: Historical validation from 2009-2024
- **Email Reports**: Detailed CSV + HTML sent to paras.m.parmar@gmail.com
- **Quarterly Rebalancing**: Seasonal adjustments (Feb end, May end, Aug end, Nov end)
- **Risk Management**: Built-in stop-loss and position sizing rules
- **Sector Rotation**: Diversification across sectors

---

## 🔧 Prerequisites

### Required:
- Python 3.10+
- GitHub account (for Actions automation)
- Gmail account (with App Password for email automation)
- NSE/BSE trading account (optional, for execution)

### Hardware:
- Minimum 2GB RAM
- 1 GB disk space
- Stable internet connection

---

## 🚀 Local Setup (Windows/Mac/Linux)

### Step 1: Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/quantitative-momentum-strategy.git
cd quantitative-momentum-strategy
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create Environment Variables
Create `.env` file in root directory:
```env
# NSE Data Settings
NIFTY_UNIVERSE=nifty_500  # or nifty_50
PORTFOLIO_SIZE=40
REBALANCE_FREQUENCY=quarterly

# Email Configuration
GMAIL_USER=your-email@gmail.com
GMAIL_PASSWORD=your-app-password
GMAIL_SERVER=smtp.gmail.com
RECIPIENT_EMAIL=paras.m.parmar@gmail.com

# Strategy Parameters
LOOKBACK_MONTHS=12
SKIP_LAST_MONTH=true
FIP_LOOKBACK_DAYS=252
STOP_LOSS_PCT=15
TARGET_PROFIT_PCT=25
```

### Step 5: Test Local Execution
```bash
python scripts/screening.py
python scripts/generate_report.py
```

---

## 🔐 Gmail Setup for Email Automation

### Step 1: Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"

### Step 2: Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows/Mac/Linux"
3. Generate password (16 characters)
4. Copy and save securely

### Step 3: Add Secrets to GitHub
1. Go to your GitHub repo
2. Settings → Secrets and variables → Actions
3. Add the following secrets:
   - `GMAIL_USER`: your-email@gmail.com
   - `GMAIL_PASSWORD`: your-16-char-app-password
   - `GMAIL_SERVER`: smtp.gmail.com

---

## ⚙️ GitHub Actions Configuration

### Step 1: Create Workflows Directory
```bash
mkdir -p .github/workflows
```

### Step 2: Add Workflow Files
Copy the following files to `.github/workflows/`:
- `daily_screening.yml` - Runs at 9:30 AM IST weekdays
- `weekly_summary.yml` - Runs Friday 6 PM IST
- `quarterly_rebalance.yml` - Quarter-end rebalance alerts

### Step 3: Verify Cron Schedule
The cron syntax uses UTC time:
- **9:30 AM IST** = **4:00 AM UTC** = `0 4 * * 1-5` (weekdays)
- **6:00 PM IST** = **12:30 PM UTC** = `30 12 * * 5` (Friday)

### Step 4: Test Workflow
1. Go to GitHub Actions tab
2. Select workflow
3. Click "Run workflow"
4. Check for successful execution

---

## 📊 Strategy Parameters (From Book)

### Entry Rules:
```
✓ Momentum Percentile: Top 10% (rank >= 90th percentile)
✓ 12-Month Lookback: Cumulative return over past 12 months
✓ Skip Last Month: Exclude last month returns (avoid reversal)
✓ FIP Quality: Prefer negative FIP scores (smooth momentum)
✓ Minimum Combined Score: > 0.5 (70% momentum, 30% quality)
✓ Rebalance Window: End of Feb, May, Aug, Nov
```

### Exit Rules:
```
✗ Stop Loss: 15% below entry price (risk limit)
✗ Target Exit: 25% above entry price (3:1 reward-risk ratio)
✗ Holding Period: Max 90 days (forced quarterly exit)
✗ Momentum Deterioration: Falls below 30th percentile
✗ FIP Degradation: FIP score becomes significantly positive
```

### Portfolio Construction:
```
Size: 40 stocks (equal-weight)
Diversification: Max 1 stock per sector rotation
Rebalance: Quarterly (4 times per year)
Trade Frequency: ~4-5 stock replacements per quarter
```

### Risk Management:
```
Position Size: 1/N where N = number of holdings (2.5% per stock)
Leverage: 1.0x (no leverage, long-only)
Max Drawdown Tolerance: 30-40% (expected based on 15-year backtest)
Sector Allocation: ~equal across sectors
```

---

## 📈 Expected Performance (15-Year Backtest)

Based on book's analysis with US data (Indian results may vary):

| Metric | Value |
|--------|-------|
| CAGR | 15.80% |
| Sharpe Ratio | 0.60 |
| Sortino Ratio | 0.72 |
| Max Drawdown | 76.97% (Great Depression) |
| Win Rate | 63% |
| Avg Trade Return | +4.5% |

---

## 📝 Output Files

### Daily Screening Results:
- `output/screening_results.csv` - All metrics in table format
- `output/report.html` - Email-friendly HTML report

### Backtest Reports:
- `output/backtest_report_15yr.html` - Historical analysis
- `output/trades_log.csv` - Complete trade history

---

## 🔍 Monitoring & Troubleshooting

### Common Issues:

#### 1. **"NSE tools not responding"**
- Fallback to yfinance (Yahoo Finance)
- Check NSE website status
- Retry connection

#### 2. **"Email not sent"**
- Verify Gmail App Password is correct
- Check GitHub Secrets configuration
- Ensure 2FA is enabled on Gmail

#### 3. **"No stocks screened"**
- Verify data availability
- Check minimum price requirements
- Ensure market is open (NSE: 9:15 AM - 3:30 PM IST)

#### 4. **Performance degradation**
- Check system resources
- Optimize data fetching (cache results)
- Reduce lookback period if needed

### Debug Mode:
```bash
# Run with verbose logging
python scripts/screening.py --verbose
python scripts/generate_report.py --debug
```

---

## 📚 Additional Resources

### Book References:
- **Primary**: "Quantitative Momentum" by Wesley R. Gray & Jack R. Vogel
- **Related**: "Quantitative Value" by Gray & Carlisle

### NSE Data Sources:
- NSEtools: https://nsepy.xyz/
- yfinance: https://finance.yahoo.com/
- Zerodha Connect (requires API key): https://zerodha.com/

### Educational Resources:
- Alpha Architect: https://alphaarchitect.com/
- NSE Official: https://www.nseindia.com/

---

## 📧 Support & Maintenance

### Weekly Maintenance:
- Review screening results quality
- Check email delivery
- Verify stock list updates

### Monthly Maintenance:
- Review strategy performance vs benchmark
- Check for data issues
- Update sector classifications

### Quarterly Maintenance:
- Rebalance portfolio
- Review entry/exit rules
- Validate 15-year backtest assumptions

---

## ⚠️ Disclaimer

- Past performance does not guarantee future results
- Momentum strategies are volatile (drawdowns: 20-75%)
- Requires discipline to follow during downturns
- Test thoroughly before live trading
- Consult financial advisor before investing

---

## 📞 Contact

For issues or improvements:
1. Open GitHub issue
2. Submit pull request
3. Email: paras.m.parmar@gmail.com

---

## 📄 License

MIT License - Free for personal and commercial use

---

## 🙏 Acknowledgments

- Wesley R. Gray & Jack R. Vogel (Book authors)
- Alpha Architect (Strategy development)
- NSE & BSE (Data providers)
- Open-source community (Tools & libraries)

---

**Last Updated**: January 2026
**Version**: 1.0.0
**Status**: Production Ready ✅
