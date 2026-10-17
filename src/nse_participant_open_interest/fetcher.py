"""NSE Participant-wise Open Interest Fetcher.

Downloads daily participant-wise derivative open interest breakdown
from archives.nseindia.com across Client, DII, FII, and Pro categories.
"""

import io
import requests
import pandas as pd
from datetime import datetime, date
from typing import Optional

NSE_PARTICIPANT_OI_URL = "https://archives.nseindia.com/content/nsccl/fao_participant_oi_{date_str}.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

class ParticipantOIFetcher:
    """Fetches and parses daily participant derivative positioning from NSE."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch_date(self, target_date: date) -> pd.DataFrame:
        """Fetch participant-wise open interest for a specific date (DDMMYYYY)."""
        date_str = target_date.strftime("%d%m%Y")
        url = NSE_PARTICIPANT_OI_URL.format(date_str=date_str)
        try:
            resp = self.session.get(url, timeout=15)
            if resp.status_code != 200:
                return pd.DataFrame()

            # The first line is a title header like 'Participant wise Open Interest ... as on Oct 16, 2026'
            df = pd.read_csv(io.StringIO(resp.text), skiprows=1)
            df.columns = [c.strip() for c in df.columns]

            if "Client Type" not in df.columns:
                return pd.DataFrame()

            # Clean and strip strings
            df["Client Type"] = df["Client Type"].astype(str).str.strip()

            # Standardize numeric columns
            numeric_cols = [c for c in df.columns if c != "Client Type"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "").str.strip(), errors="coerce").fillna(0).astype("int64")

            # Map to clean snake_case schema
            column_map = {
                "Client Type": "client_type",
                "Future Index Long": "future_index_long",
                "Future Index Short": "future_index_short",
                "Future Stock Long": "future_stock_long",
                "Future Stock Short": "future_stock_short",
                "Option Index Call Long": "option_index_call_long",
                "Option Index Put Long": "option_index_put_long",
                "Option Index Call Short": "option_index_call_short",
                "Option Index Put Short": "option_index_put_short",
                "Option Stock Call Long": "option_stock_call_long",
                "Option Stock Put Long": "option_stock_put_long",
                "Option Stock Call Short": "option_stock_call_short",
                "Option Stock Put Short": "option_stock_put_short",
                "Total Long Contracts": "total_long_contracts",
                "Total Short Contracts": "total_short_contracts"
            }
            renamed = df.rename(columns=column_map)

            # Add metadata
            renamed["trade_date"] = target_date.strftime("%Y-%m-%d")
            renamed["source"] = "NSE_FAO_PARTICIPANT_OI"

            # Filter for valid participant rows
            valid_participants = ["Client", "DII", "FII", "Pro", "TOTAL"]
            renamed = renamed[renamed["client_type"].isin(valid_participants)].copy()

            # Derived positioning metrics per participant
            renamed["net_future_index"] = renamed["future_index_long"] - renamed["future_index_short"]
            renamed["net_future_stock"] = renamed["future_stock_long"] - renamed["future_stock_short"]

            tot_fut_idx = renamed["future_index_long"] + renamed["future_index_short"]
            renamed["future_index_long_pct"] = (renamed["future_index_long"] / tot_fut_idx * 100.0).round(2).fillna(0.0)

            # Reorder columns
            cols_order = [
                "trade_date", "client_type",
                "future_index_long", "future_index_short", "net_future_index", "future_index_long_pct",
                "future_stock_long", "future_stock_short", "net_future_stock",
                "option_index_call_long", "option_index_put_long",
                "option_index_call_short", "option_index_put_short",
                "option_stock_call_long", "option_stock_put_long",
                "option_stock_call_short", "option_stock_put_short",
                "total_long_contracts", "total_short_contracts",
                "source"
            ]
            return renamed[cols_order]

        except Exception as e:
            print(f"Error fetching participant OI for {target_date}: {e}")
            return pd.DataFrame()
