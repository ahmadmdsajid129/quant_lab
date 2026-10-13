# QuantLab Market Data Infrastructure & Provider Evaluations

**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Classification:** Data Architecture & External Integrations  

---

## 1. Provider Evaluation & Strategy

QuantLab enforces a **provider-agnostic adapter architecture**. Research components interact exclusively with standardized internal schemas, shielding strategies and backtesting engines from external provider idiosyncrasies.

| Provider | Asset Classes | Granularity | Auth / Tier | Licensing / Rate Limits | QuantLab Integration Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Synthetic Market Data Generator** | Equities, Crypto, FX, Indices | 1m, 5m, 1h, 1D | None (Internal) | Unlimited, zero dependency | **Core Default**: Guaranteed reproducible offline baseline using Geometric Brownian Motion with Jump Diffusion and GARCH volatility clustering. |
| **Stooq** | Equities, ETFs, FX, Indices (Global) | Daily (1D) | None (Public CSV) | Free for academic/personal research. No API key needed. | **Tier 1 Free Live Adapter**: Default public data adapter for global equities (US, UK, Poland, Germany) and FX pairs. |
| **Yahoo Finance (via yfinance / direct)** | Equities, ETFs, Indices, Options | 1m (last 7d) to 1D | None (Unofficial) | Personal use only; subject to rate throttling and schema shifts. | **Tier 2 Live Adapter**: Fallback with robust request retries, caching, and rate limiting. |
| **FRED (St. Louis Fed)** | Macroeconomic, Risk-Free Rates (SOFR, Treasury yields) | Daily / Monthly | Free API Key | Public domain US government data. | **Macro Adapter**: Supplies historical risk-free benchmark series ($r_f$) for Sharpe calculations. |
| **Alpha Vantage / Tiingo** | Equities, Crypto, FX | 1m to 1D | Free/Paid API Key | 5 calls/min (Alpha Vantage free tier). | **Optional Adapter**: Configurable via workspace environment credentials. |
| **Public Crypto (Binance / Coinbase)** | Cryptocurrency spot & futures | Tick, 1m, L2 Order Book | Public REST & WS | High rate limits for public order books and historical klines. | **Microstructure Adapter**: Supplies real L2 snapshots and trade flows. |

---

## 2. Standardized Data Schemas

All raw ingested data must be normalized into internal Pydantic/Parquet schemas prior to persistence.

### 2.1 Standard Bar Schema (OHLCV)
```python
class NormalizedBar:
    timestamp: datetime       # UTC timestamp (bar end or start explicitly flagged)
    symbol: str               # Canonical symbol (e.g., 'AAPL', 'SPY', 'BTC-USD')
    open: float               # Open price (split/dividend adjusted if applicable)
    high: float               # High price
    low: float                # Low price
    close: float              # Close price
    volume: float             # Traded volume
    vwap: Optional[float]     # Volume-weighted average price
    trades_count: Optional[int] # Number of trades during bar
```

### 2.2 Standard Order Book Snapshot Schema (L2)
```python
class OrderBookSnapshot:
    timestamp: datetime       # UTC microsecond precision
    symbol: str
    bids: List[Tuple[float, float]] # Sorted descending: [(price, size), ...]
    asks: List[Tuple[float, float]] # Sorted ascending: [(price, size), ...]
```

---

## 3. Data Quality & Audit Framework

Every dataset import automatically runs a standardized 5-point QA audit:
1. **Timestamp Continuity**: Detects missing trading days or unexpected time gaps against market exchange calendars (e.g. NYSE/NASDAQ holidays).
2. **Price Sanity**: Verifies $High \ge \max(Open, Close)$ and $Low \le \min(Open, Close)$. Rejects negative prices.
3. **Anomaly & Spike Detection**: Flags daily percentage returns exceeding threshold (e.g. $> 50\%$) as potential unadjusted splits.
4. **Volume Integrity**: Rejects negative volumes; warns on extended zero-volume periods.
5. **Corporate Action Adjustment**: Verifies split and dividend ratios against unadjusted raw series.

Datasets that pass the audit receive a `QUALITY_VERIFIED` badge with a data quality score ($0-100\%$).

---

## 4. Built-in Synthetic Market Data Generator

To guarantee that QuantLab can be verified, demonstrated, and tested in any environment without external internet access or credentials, QuantLab includes an institutional-grade **Synthetic Market Data Generator**:
- **Stochastic Model**: Jump-Diffusion model:
  $$dS_t = \mu S_t dt + \sigma S_t dW_t + J_t S_t dN_t$$
  where $W_t$ is a Wiener process, $N_t$ is a Poisson jump process with intensity $\lambda$, and $J_t$ is the jump size.
- **Configurable Parameters**: Drift $\mu$, Volatility $\sigma$, Jump frequency, Mean reversion speed, Correlation matrix for multi-asset universes.
- **Reproducibility**: Parameterized by an explicit integer `seed` ensuring identical data frames across runs.
