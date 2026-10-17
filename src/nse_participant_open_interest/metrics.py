"""Participant Open Interest Macro & Sentiment Evaluator."""

import pandas as pd
from typing import Dict, Any

class ParticipantOIEvaluator:
    """Evaluates smart money derivative positioning and market sentiment regimes."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def get_latest_summary(self, as_of_date: str = None) -> Dict[str, Any]:
        """Returns macro summary of FII vs Retail derivatives stance."""
        df_target = self.df
        if as_of_date:
            df_target = df_target[df_target["trade_date"] == as_of_date]
        else:
            latest_date = df_target["trade_date"].max()
            df_target = df_target[df_target["trade_date"] == latest_date]

        fii_row = df_target[df_target["client_type"] == "FII"]
        client_row = df_target[df_target["client_type"] == "Client"]
        pro_row = df_target[df_target["client_type"] == "Pro"]
        dii_row = df_target[df_target["client_type"] == "DII"]

        if fii_row.empty:
            return {}

        fii = fii_row.iloc[0]
        client = client_row.iloc[0] if not client_row.empty else None

        fii_long_pct = float(fii["future_index_long_pct"])
        fii_net_idx = int(fii["net_future_index"])

        # Volatility & positioning regime
        if fii_long_pct < 20.0:
            regime = "EXTREME_BEARISH_FII_OVERSOLD"
        elif fii_long_pct < 40.0:
            regime = "BEARISH_FII_CAUTIOUS"
        elif fii_long_pct <= 65.0:
            regime = "NEUTRAL_BALANCED"
        elif fii_long_pct <= 80.0:
            regime = "BULLISH_FII"
        else:
            regime = "EXTREME_BULLISH_FII_OVERHEATED"

        return {
            "trade_date": fii["trade_date"],
            "fii_index_future_long_pct": fii_long_pct,
            "fii_net_index_futures": fii_net_idx,
            "fii_net_stock_futures": int(fii["net_future_stock"]),
            "client_index_future_long_pct": float(client["future_index_long_pct"]) if client is not None else 0.0,
            "client_net_index_futures": int(client["net_future_index"]) if client is not None else 0,
            "market_regime": regime
        }
