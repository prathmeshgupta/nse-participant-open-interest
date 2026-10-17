# NSE Participant Open Interest & Smart Money Positioning

[![Daily/Weekly Participant OI Dataset Update](https://github.com/prathmeshgupta/nse-participant-open-interest/actions/workflows/weekly_update.yml/badge.svg)](https://github.com/prathmeshgupta/nse-participant-open-interest/actions/workflows/weekly_update.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Institutional time-series dataset of National Stock Exchange of India (NSE) daily **participant-wise derivative open interest (OI)** across **FII, DII, Proprietary Desks (Pro), and Retail (Client)**.

Captures institutional smart-money leverage, long-short index future ratios, and option gamma exposures for quantitative market-timing and volatility regime models.

---

### The Quantitative Problem

In the Indian equity derivatives market (the largest by contracts globally), market sentiment and directional tail-risk are heavily governed by **Foreign Portfolio Investors (FII)** and **Prop Desks (Pro)** executing against retail traders:

1. **FII Long-Short Index Ratio:** When FII net index futures long % drops below **20%**, the market is statistically in an extreme oversold zone prone to violent short squeezes. Above **75%**, the market is frothy and vulnerable to cascading liquidations.
2. **Retail vs Institutional Option Positioning:** Retail traders systematically buy out-of-the-money options (net long calls/puts), while prop desks and institutions write options (net short calls/puts) capturing theta and implied volatility risk premiums.

This dataset aggregates and audits official daily participant positioning archives (`fao_participant_oi_*.csv`) published by NSE/NSCCL.

---

### Dataset Schema

Outputs are distributed in both **Apache Parquet (`snappy` compressed)** and standard **CSV**:
* `output/participant_oi.parquet`
* `output/participant_oi.csv`
* `output/macro_fii_positioning.csv` (High-level daily summary)

| Field | Type | Description |
| :--- | :--- | :--- |
| `trade_date` | `string` | Trade session date in `YYYY-MM-DD` |
| `client_type` | `string` | Participant category (`FII`, `DII`, `Pro`, `Client`, `TOTAL`) |
| `future_index_long` | `int64` | Open interest in Index Futures (Nifty, BankNifty, etc.) - Long |
| `future_index_short` | `int64` | Open interest in Index Futures - Short |
| `net_future_index` | `int64` | Net Index Futures contracts (`Long - Short`) |
| `future_index_long_pct` | `float` | Percentage of Index Futures position that is Long (`0.0%` to `100.0%`) |
| `future_stock_long` | `int64` | Open interest in Single-Stock Futures - Long |
| `future_stock_short` | `int64` | Open interest in Single-Stock Futures - Short |
| `net_future_stock` | `int64` | Net Single-Stock Futures contracts (`Long - Short`) |
| `option_index_call_long` | `int64` | Index Call Options open interest - Long |
| `option_index_put_long` | `int64` | Index Put Options open interest - Long |
| `option_index_call_short` | `int64` | Index Call Options open interest - Short |
| `option_index_put_short` | `int64` | Index Put Options open interest - Short |
| `option_stock_call_long` | `int64` | Stock Call Options open interest - Long |
| `option_stock_put_long` | `int64` | Stock Put Options open interest - Long |
| `option_stock_call_short` | `int64` | Stock Call Options open interest - Short |
| `option_stock_put_short` | `int64` | Stock Put Options open interest - Short |
| `total_long_contracts` | `int64` | Aggregate long derivative contracts held |
| `total_short_contracts`| `int64` | Aggregate short derivative contracts held |
| `source` | `string` | Data source origin (`NSE_FAO_PARTICIPANT_OI`) |

---

### Automated Weekly & Daily Updates

* **Schedule**: Automated GitHub Actions workflow executes at **14:30 UTC (20:00 IST) Monday to Friday**, with weekly Sunday reconciliation at **02:00 UTC**.
* **Self-Healing Gap Fill**: Reads `MAX(trade_date)` and automatically loops to backfill any missing trading sessions.
* **Accounting Validation Gate**: Enforces the derivatives clearing identity: `TOTAL Long == TOTAL Short` across every session.

---

### Quickstart & CLI Usage

```bash
# 1. Clone the repository
git clone https://github.com/prathmeshgupta/nse-participant-open-interest.git
cd nse-participant-open-interest

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the automated updater locally
python update.py

# 4. View latest smart-money positioning regime
python runner.py --summary

# 5. Query a specific trade date
python runner.py --date 2026-10-16
```
