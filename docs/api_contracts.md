# QuantLab REST API Contracts & Endpoint Specifications

**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Base Path:** `/api/v1`  
**Classification:** Core Interface Contract  

---

## 1. General Conventions

- **Protocol**: HTTP/1.1 and HTTP/2 over TLS; WebSocket for real-time order book / paper trading.
- **Content-Type**: `application/json` (except binary exports like Parquet, CSV, or PDF).
- **Authentication**: Bearer Token in `Authorization` header (`Authorization: Bearer <jwt_token>`).
- **Standard Date Format**: ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`).
- **Standard Pagination**:
  ```json
  {
    "items": [...],
    "total": 142,
    "page": 1,
    "size": 50,
    "pages": 3
  }
  ```
- **Standard Error Schema**:
  ```json
  {
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Start date must precede end date",
      "details": {"field": "end_date", "reason": "invalid_range"}
    }
  }
  ```

---

## 2. Endpoint Families Specification

### 2.1 Authentication & Workspaces (`/auth`, `/workspaces`)
- `POST /api/v1/auth/register`: Register new user (`email`, `password`, `full_name`). Returns `201 Created` with default workspace.
- `POST /api/v1/auth/login`: Authenticate with `email` and `password`. Returns `200 OK` with `{access_token, token_type: "bearer", user}`.
- `GET /api/v1/auth/me`: Current authenticated user profile, permissions, and active workspace.
- `GET /api/v1/workspaces`: List workspaces accessible to user.
- `POST /api/v1/workspaces`: Create team or personal workspace.

### 2.2 Research Projects & Hypotheses (`/projects`)
- `GET /api/v1/projects`: List projects in active workspace (filters: `status`, `asset_class`).
- `POST /api/v1/projects`: Create project (`title`, `description`, `asset_class`, `tags`).
- `GET /api/v1/projects/{id}`: Detailed project information, including hypotheses, experiment history, and latest metrics.
- `POST /api/v1/projects/{id}/hypotheses`: Add structured hypothesis (`statement`, `mechanism`, `prediction`, `falsification_criteria`).
- `POST /api/v1/projects/{id}/notes`: Add rich Markdown research note.

### 2.3 Market Data Infrastructure (`/datasets`)
- `GET /api/v1/datasets`: List available datasets (source, symbols, start/end dates, quality score).
- `POST /api/v1/datasets/import`: Trigger ingestion job (`provider: "stooq"|"synthetic"|"csv"`, `symbol`, `start_date`, `end_date`).
- `POST /api/v1/datasets/generate-synthetic`: Generate deterministic GBM/jump-diffusion synthetic dataset (`symbols`, `days`, `volatility`, `drift`, `seed`).
- `GET /api/v1/datasets/{id}/ohlcv`: Fetch paginated OHLCV bars for charting.
- `GET /api/v1/datasets/{id}/quality-audit`: Retrieve automated 5-point data quality audit report.

### 2.4 Exploratory Analytics (`/analytics`)
- `POST /api/v1/analytics/returns`: Compute simple, log, and rolling returns for symbol.
- `POST /api/v1/analytics/volatility`: Compute rolling annualized volatility.
- `POST /api/v1/analytics/distribution`: Compute skewness, kurtosis, Jarque-Bera, and ADF stationarity test.
- `POST /api/v1/analytics/correlation`: Pairwise correlation matrix across multiple instruments.

### 2.5 Strategy & Backtesting Engine (`/strategies`, `/backtests`)
- `GET /api/v1/strategies/templates`: Retrieve built-in educational templates (MA Crossover, Momentum, Mean Reversion).
- `POST /api/v1/backtests/run`: Submit backtest job:
  ```json
  {
    "project_id": "uuid",
    "dataset_id": "uuid",
    "strategy_type": "ma_crossover",
    "parameters": {"fast_period": 20, "slow_period": 50},
    "capital": 100000.0,
    "commission_bps": 5.0,
    "slippage_pct": 0.05,
    "execution_model": "next_open",
    "borrow_rate_pct": 2.0
  }
  ```
  Returns `202 Accepted` with `{job_id, status: "QUEUED"}`.
- `GET /api/v1/backtests/{id}`: Retrieve backtest results: summary metrics, equity curve array, drawdown array, trade logs, and cost breakdown.

### 2.6 Statistical Validation Laboratory (`/validation`)
- `POST /api/v1/validation/walk-forward`: Execute rolling or expanding walk-forward train/test analysis.
- `POST /api/v1/validation/purged-kfold`: Purged K-fold cross-validation with embargo.
- `POST /api/v1/validation/bootstrap`: Stationary block bootstrap confidence intervals for Sharpe and mean returns.
- `POST /api/v1/validation/deflated-sharpe`: Compute Deflated Sharpe Ratio (DSR) given backtest Sharpe, variance, skew, kurtosis, and total number of trials.

### 2.7 Machine Learning Laboratory (`/ml`)
- `POST /api/v1/ml/features`: Generate time-lagged, rolling momentum, and volatility features.
- `POST /api/v1/ml/train`: Train model (`model_type: "ridge"|"rf"|"gbdt"`, `train_ratio`, `hyperparameters`).
- `GET /api/v1/ml/{id}/shap`: Retrieve SHAP feature importance values and summary curves.
- `POST /api/v1/ml/{id}/drift`: Compute Kolmogorov-Smirnov distribution drift test between train and test features.

### 2.8 Portfolio Optimization & Risk (`/portfolio`, `/risk`)
- `POST /api/v1/portfolio/optimize`: Run portfolio optimization:
  - Methods: `equal_weight`, `inverse_volatility`, `risk_parity`, `max_sharpe`, `min_volatility`.
  - Covariance estimators: `sample`, `ledoit_wolf`.
  - Constraints: `long_only`, `max_weight`, `target_return`.
- `POST /api/v1/risk/stress-test`: Run historical and custom scenario stress tests.
- `POST /api/v1/risk/var-cvar`: Compute historical and parametric VaR and CVaR at 95% and 99% confidence.

### 2.9 Market Microstructure & LOB Simulator (`/microstructure`)
- `POST /api/v1/microstructure/init`: Initialize order book for symbol with custom tick size.
- `GET /api/v1/microstructure/snapshot`: Get current L2/L3 order book depth (Bids & Asks ladder).
- `POST /api/v1/microstructure/order`: Submit limit or market order (`side`, `price`, `quantity`, `order_type`).
- `POST /api/v1/microstructure/simulate-flow`: Run synthetic Hawkes/Poisson order flow for $N$ events and return execution statistics.

### 2.10 Options & Derivatives Laboratory (`/options`)
- `POST /api/v1/options/price`: Compute European Call/Put price and Greeks (Delta, Gamma, Theta, Vega, Rho) via Black-Scholes-Merton.
- `POST /api/v1/options/binomial`: Compute American option price via CRR binomial tree.
- `POST /api/v1/options/implied-volatility`: Solve implied volatility from observed market option price.
- `POST /api/v1/options/payoff`: Generate multi-leg strategy payoff profile (Straddle, Bull Spread, Iron Condor).

### 2.11 AI Research Copilot (`/copilot`)
- `POST /api/v1/copilot/chat`: Context-grounded query regarding project, backtest runs, or methodologies.
- `POST /api/v1/copilot/review-methodology`: Systematic audit of strategy parameters and validation for potential leakage or overfitting.

### 2.12 Paper Trading & Jobs (`/paper-trading`, `/jobs`)
- `GET /api/v1/paper-trading/portfolio`: Get virtual cash, open positions, unrealized PnL, margin utilization.
- `POST /api/v1/paper-trading/order`: Submit paper trading order with pre-trade risk verification.
- `GET /api/v1/jobs`: List background jobs with status, progress %, and execution times.
- `POST /api/v1/jobs/{id}/cancel`: Request cancellation of active background compute job.
