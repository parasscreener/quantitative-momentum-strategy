"""
Check if today is a rebalance date
Used by quarterly rebalance workflow
"""

from datetime import datetime

def check_if_rebalance_date():
    """
    Check if current date is a quarter-end rebalance date
    Rebalance dates: Last day of Feb, May, Aug, Nov
    """

    today = datetime.now()
    year = today.year

    rebalance_dates = [
        datetime(year, 2, 28) if year % 4 != 0 else datetime(year, 2, 29),  # Feb (29 if leap year)
        datetime(year, 5, 31),   # May
        datetime(year, 8, 31),   # Aug
        datetime(year, 11, 30),  # Nov
    ]

    print(f"Today: {today.strftime('%Y-%m-%d')}")
    print(f"Rebalance Dates for {year}:")
    for date in rebalance_dates:
        print(f"  - {date.strftime('%Y-%m-%d')}")

    if today.date() in [d.date() for d in rebalance_dates]:
        print(f"\n✅ TODAY IS A REBALANCE DATE!")
        return True
    else:
        print(f"\n❌ Not a rebalance date")
        return False

if __name__ == "__main__":
    check_if_rebalance_date()
