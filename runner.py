"""CLI Tool for NSE Participant Open Interest.

Usage:
    python runner.py --summary
    python runner.py --date 2026-10-16
"""

import argparse
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from nse_participant_open_interest.metrics import ParticipantOIEvaluator

def main():
    parser = argparse.ArgumentParser(description="NSE Participant Open Interest CLI")
    parser.add_argument("--summary", action="store_true", help="Show latest smart-money positioning regime")
    parser.add_argument("--date", help="Query specific trade date (YYYY-MM-DD)")
    args = parser.parse_args()

    parquet_path = Path(__file__).parent / "output" / "participant_oi.parquet"
    if not parquet_path.exists():
        print("Dataset not found. Run python update.py first.")
        return

    df = pd.read_parquet(parquet_path)
    evaluator = ParticipantOIEvaluator(df)

    target_date = args.date or df["trade_date"].max()
    date_df = df[df["trade_date"] == target_date]

    if date_df.empty:
        print(f"No records found for date {target_date}.")
        return

    print(f"\n=========================================================================================")
    print(f" NSE PARTICIPANT OPEN INTEREST POSITIONING AS OF {target_date}")
    print(f"=========================================================================================")
    cols = ["client_type", "future_index_long", "future_index_short", "net_future_index", "future_index_long_pct", "net_future_stock", "total_long_contracts", "total_short_contracts"]
    print(date_df[cols].to_string(index=False))

    summary = evaluator.get_latest_summary(target_date)
    if summary:
        print(f"\n--- Smart Money Positioning & Regime ---")
        print(f"  * FII Index Futures Long %  : {summary['fii_index_future_long_pct']:.2f}%")
        print(f"  * FII Net Index Futures     : {summary['fii_net_index_futures']:,} contracts")
        print(f"  * FII Net Stock Futures     : {summary['fii_net_stock_futures']:,} contracts")
        print(f"  * Client (Retail) Long %    : {summary['client_index_future_long_pct']:.2f}%")
        print(f"  * Market Regime Assessment  : {summary['market_regime']}")
    print(f"=========================================================================================\n")

if __name__ == "__main__":
    main()
