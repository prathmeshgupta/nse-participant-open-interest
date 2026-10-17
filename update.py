"""NSE Participant Open Interest Weekly/Daily Automated Updater.

Self-healing gap-fill updater that fetches daily participant-wise derivative
open interest from NSE archives, computes smart-money positioning metrics,
and writes Parquet and CSV outputs atomically.
"""

import sys
from datetime import datetime, date, timedelta
from pathlib import Path
import pandas as pd

# Add local src to path for direct execution
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from nse_participant_open_interest.fetcher import ParticipantOIFetcher

def get_trading_days(start_date: date, end_date: date) -> list[date]:
    """Generate potential trading weekdays between start and end date inclusive."""
    days = []
    curr = start_date
    while curr <= end_date:
        if curr.weekday() < 5:  # Monday to Friday
            days.append(curr)
        curr += timedelta(days=1)
    return days

def update_participant_oi():
    print(f"[{datetime.now().isoformat()}] Starting Participant Open Interest update...")
    fetcher = ParticipantOIFetcher()
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_file = output_dir / "participant_oi.csv"
    parquet_file = output_dir / "participant_oi.parquet"
    summary_csv = output_dir / "macro_fii_positioning.csv"

    existing_df = pd.DataFrame()
    if parquet_file.exists():
        existing_df = pd.read_parquet(parquet_file)
        print(f"Loaded {len(existing_df):,} existing records from {parquet_file.name}")

    today = date.today()

    if existing_df.empty:
        # Initial seed: Last 7 days
        start_date = today - timedelta(days=7)
    else:
        max_date_str = str(existing_df["trade_date"].max())
        max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
        start_date = max_date - timedelta(days=1)

    target_days = get_trading_days(start_date, today)
    print(f"Targeting {len(target_days)} trading days between {start_date} and {today}...")

    new_dfs = []
    for d in target_days:
        print(f"Fetching participant OI for {d.strftime('%Y-%m-%d')}...")
        df_day = fetcher.fetch_date(d)
        if not df_day.empty:
            print(f"  Successfully parsed {len(df_day)} participant records.")
            new_dfs.append(df_day)
        else:
            print(f"  No participant OI data available for {d.strftime('%Y-%m-%d')} (holiday or not yet published).")

    if not new_dfs and existing_df.empty:
        raise RuntimeError("No participant OI data could be retrieved and no existing database found.")

    combined = list(new_dfs)
    if not existing_df.empty:
        combined.insert(0, existing_df)

    merged = pd.concat(combined, ignore_index=True)

    # Core key deduplication
    merged = merged.drop_duplicates(subset=["trade_date", "client_type"], keep="last")

    # Sort chronologically descending
    client_order = {"FII": 1, "DII": 2, "Pro": 3, "Client": 4, "TOTAL": 5}
    merged["client_sort"] = merged["client_type"].map(client_order).fillna(99)
    merged = merged.sort_values(by=["trade_date", "client_sort"], ascending=[False, True]).drop(columns=["client_sort"]).reset_index(drop=True)

    # Save main datasets
    merged.to_parquet(parquet_file, index=False, compression="snappy")
    merged.to_csv(csv_file, index=False)
    print(f"Saved {len(merged):,} records to {parquet_file.name} and {csv_file.name}")

    # Generate quick macro summary table for FII vs Retail
    fii_df = merged[merged["client_type"] == "FII"][["trade_date", "future_index_long", "future_index_short", "net_future_index", "future_index_long_pct", "net_future_stock"]]
    client_df = merged[merged["client_type"] == "Client"][["trade_date", "future_index_long_pct", "net_future_index"]].rename(columns={"future_index_long_pct": "client_long_pct", "net_future_index": "client_net_index"})
    summary = pd.merge(fii_df, client_df, on="trade_date", how="left")
    summary.to_csv(summary_csv, index=False)
    print(f"Saved macro FII vs Retail positioning summary to {summary_csv.name}")

    # Run quality gate
    from evaluate_quality import audit_quality
    audit_quality()
    print("Participant Open Interest update completed successfully.")

if __name__ == "__main__":
    update_participant_oi()
