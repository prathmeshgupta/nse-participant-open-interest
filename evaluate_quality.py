"""Quality and Accounting Audit for NSE Participant Open Interest Dataset."""

import pandas as pd
from pathlib import Path

def audit_quality():
    print("=" * 65)
    print(" NSE PARTICIPANT OPEN INTEREST - DATA QUALITY AUDIT")
    print("=" * 65)

    parquet_path = Path(__file__).parent / "output" / "participant_oi.parquet"
    assert parquet_path.exists(), f"Missing {parquet_path.name}"

    df = pd.read_parquet(parquet_path)
    print(f"Total Participant Rows Indexed: {len(df):,}")

    # Null checks
    null_dates = df["trade_date"].isnull().sum()
    null_types = df["client_type"].isnull().sum()
    print(f"Null Trade Dates: {null_dates} {'[PASS]' if null_dates == 0 else '[FAIL]'}")
    print(f"Null Client Types: {null_types} {'[PASS]' if null_types == 0 else '[FAIL]'}")

    # Accounting Identity: For each trade_date, Total Long Contracts == Total Short Contracts on TOTAL row
    total_rows = df[df["client_type"] == "TOTAL"]
    mismatch_totals = (total_rows["total_long_contracts"] != total_rows["total_short_contracts"]).sum()
    print(f"Contract Balance Identity (TOTAL Long == TOTAL Short): {mismatch_totals} {'[PASS]' if mismatch_totals == 0 else '[FAIL]'}")

    # Participant breakdown completeness
    distinct_dates = df["trade_date"].nunique()
    print(f"Distinct Trading Dates Covered: {distinct_dates}")

    assert null_dates == 0, "Null trade dates detected!"
    assert null_types == 0, "Null client types detected!"
    assert mismatch_totals == 0, "Total contracts long != short on TOTAL row!"

    print("=" * 65)
    print("ALL AUDIT CHECKS PASSED.")
    print("=" * 65)

if __name__ == "__main__":
    audit_quality()
