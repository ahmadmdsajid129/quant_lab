# QuantLab — Institutional Quantitative Research Workstation

[![Automated Tests](https://img.shields.io/badge/Tests-45%2F45%20Passing-brightgreen.svg)](docs/testing_strategy.md)
[![Frontend](https://img.shields.io/badge/Next.js-14%20App%20Router-black.svg)](frontend/)
[![Backend](https://img.shields.io/badge/FastAPI-Python%203.13-009688.svg)](backend/)
[![Storage](https://img.shields.io/badge/Storage-Parquet%20%2B%20SQLAlchemy%202.0-blue.svg)](backend/app/db/)
[![Quantitative Rigor](https://img.shields.io/badge/Invariants-Zero%20Lookahead%20%7C%20Zero%20Leakage-critical.svg)](docs/rules.md)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**QuantLab** is a unified, institutional-grade quantitative research, backtesting, and experimentation platform for financial markets.

It bridges the gap between ad-hoc scientific notebooks and production algorithmic execution by integrating hypothesis formulation, market data ingestion, exploratory analytics, event-driven backtesting, statistical robustness validation, financial machine learning, portfolio risk optimization, Limit Order Book (LOB) microstructure simulation, options pricing, and evidence-grounded AI copilot assistance into a single unified workstation.

---

## Table of Contents

- [Core Principles & Quantitative Invariants](#core-principles--quantitative-invariants)
- [System Architecture](#system-architecture)
- [Workstation Modules & UI Views](#workstation-modules--ui-views)
- [Repository Layout](#repository-layout)
- [End-to-End Research Lifecycle](#end-to-end-research-lifecycle)
- [REST API Specifications](#rest-api-specifications)
- [Getting Started & Quickstart](#getting-started--quickstart)
  - [Prerequisites](#prerequisites)
  - [Backend Setup (FastAPI & Python 3.13)](#backend-setup-fastapi--python-313)
  - [Frontend Setup (Next.js 14 & Tailwind CSS)](#frontend-setup-nextjs-14--tailwind-css)
- [Automated Verification & Test Suite](#automated-verification--test-suite)
- [Canonical Documentation Suite](#canonical-documentation-suite)
- [License & Acknowledgments](#license--acknowledgments)

---

## Core Principles & Quantitative Invariants

QuantLab enforces strict econometric, mathematical, and algorithmic invariants across every layer of the compute engine:

### 1. Strict $t \to t+1$ Time Semantics (Zero Look-Ahead Bias)
Signals computed from bar $t$ close are strictly forbidden from executing at bar $t$ close. All orders transition to pending state and fill against bar $t+1$ Open prices with explicit slippage modeling and fee deductions:
$$\text{Execution Price} = \text{Open}_{t+1} \times (1 \pm \delta_{\text{slippage}})$$
$$\text{Cash Balance}_{t+1} = \text{Cash}_t - (\text{Price} \times \text{Qty}) - \text{Fees}$$

### 2. Zero Preprocessing Data Leakage in Machine Learning
Financial time-series features are scaled and transformed strictly using parameters fitted on the chronological training partition. Test sets are transformed using historical training distributions—never global samples:
$$\mu_{\text{train}}, \sigma_{\text{train}} = \text{fit}(X_{1 \dots T_{\text{split}}})$$
$$X_{\text{test}}^{\text{scaled}} = \frac{X_{T_{\text{split}}+1 \dots T} - \mu_{\text{train}}}{\sigma_{\text{train}}}$$

### 3. Deflated Sharpe Ratio (DSR) & Multiple Testing Correction
Following **Bailey & López de Prado (2014)**, observed strategy performance is adjusted for selection bias over $N$ parameter trials and non-normal return distributions (skewness $\gamma_1$ and excess kurtosis $\gamma_2$):
$$\text{DSR} = Z\left[ \frac{(\widehat{\text{SR}} - \text{SR}^*) \sqrt{T-1}}{\sqrt{1 - \gamma_1 \widehat{\text{SR}} + \frac{\gamma_2 - 1}{4} \widehat{\text{SR}}^2}} \right]$$
where $\text{SR}^*$ represents the expected maximum Sharpe ratio hurdle under the null hypothesis of false discovery.

### 4. Euler Marginal Risk Contribution Decomposition
Multi-asset portfolio volatility decomposes exactly into constituent marginal risk contributions with zero residual:
$$\sigma_p = \sqrt{w^T \Sigma w}, \quad \text{MRC}_i = \frac{(\Sigma w)_i}{\sigma_p}, \quad \text{RC}_i = w_i \times \text{MRC}_i \implies \sum_{i=1}^N \text{RC}_i = \sigma_p$$
Covariance matrices are estimated using **Ledoit-Wolf optimal shrinkage** toward constant correlation to guarantee condition-number stability.

### 5. Double-Auction Price-Time Priority LOB Matching Engine
Microstructure simulations implement true Price-Time Priority queue dynamics. Resting orders join discrete FIFO price buckets, while crossing orders execute immediately with deterministic price improvement.

### 6. Analytical Derivatives & Put-Call Parity Invariants
Analytical Black-Scholes pricing strictly adheres to continuous Put-Call Parity:
$$C(S, K, T) - P(S, K, T) = S e^{-qT} - K e^{-rT} \quad (|\Delta| < 10^{-4})$$
CRR Binomial Tree models converge monotonically to analytical Black-Scholes values as step count $N \to \infty$.

---

## System Architecture

```text
+---------------------------------------------------------------------------------------+
|                               QUANTLAB WORKSTATION UI                                 |
|                     Next.js 14 App Router | React | Tailwind CSS                      |
|  Projects | Datasets | EDA | Backtest | Validation | ML | Portfolio | LOB | Options  |
+-------------------------------------------+-------------------------------------------+
                                            | REST / JSON
                                            v
+---------------------------------------------------------------------------------------+
|                               FASTAPI WORKSTATION ENGINE                              |
|         Async API Routing | Pydantic V2 Validation | JWT RBAC Security Layer          |
+-------------------------------------------+-------------------------------------------+
         |                                  |                                  |
         v                                  v                                  v
+------------------+              +-------------------+              +------------------+
| QUANT ENGINE     |              | AI COPILOT        |              | BACKGROUND JOBS  |
| - Event Backtest |              | - Context Graph   |              | - Task Queue     |
| - Deflated SR    |              | - Methodology QA  |              | - Process Mon    |
| - ML Pipelines   |              | - Research Notes  |              | - Cancellation   |
| - Ledoit-Wolf    |              +-------------------+              +------------------+
| - LOB Matching   |
| - Black-Scholes  |
+------------------+
         |
         +----------------------------------+
         |                                  |
         v                                  v
+--------------------------------+ +--------------------------------+
|      RELATIONAL METADATA       | |      COLUMNAR TIME SERIES      |
|    SQLAlchemy 2.0 / SQLite     | |    Apache Parquet Datasets     |
| Projects, Hypotheses, Trades   | |  OHLCV Bars, Quotes, Depth     |
+--------------------------------+ +--------------------------------+
```

---

## Workstation Modules & UI Views

The Next.js 14 frontend provides 17 institutional workstation pages:

1. **Dashboard (`/`)**: System overview, active research telemetry, running backtests, and recent tearsheets.
2. **Research Projects (`/projects`)**: Workspace project formulation and asset class tracking.
3. **Project Workspace (`/projects/[id]`)**: Hypothesis definition (economic mechanism, falsification criteria), research notes, and experiment history.
4. **Market Data & QA (`/data`)**: Merton Jump-Diffusion synthetic generator, Parquet registry, and 5-point data quality audit reports.
5. **Exploratory Analytics (`/analytics`)**: Statistical moments (mean, vol, skew, kurtosis), Jarque-Bera normality tests, ADF stationarity, and ACF autocorrelation.
6. **Strategy Backtester (`/backtests`)**: Event-driven execution configuration ($t \to t+1$ time semantics), equity curves, drawdown series, and financial KPIs.
7. **Statistical Validation (`/validation`)**: Deflated Sharpe Ratio ($SR^*$), Purged K-Fold with embargo, and Walk-Forward Efficiency (WFE) analysis.
8. **Machine Learning Lab (`/ml`)**: Feature pipeline (momentum, volatility, RSI, MACD), chronological train-only scaling, model training, and Kolmogorov-Smirnov drift diagnostics.
9. **Portfolio Optimization (`/portfolio`)**: Max Sharpe, GMV, Equal Risk Parity (ERP), Ledoit-Wolf shrinkage, and Euler marginal risk contribution bar charts.
10. **Market Microstructure (`/microstructure`)**: Double-auction LOB simulator, Level 2 depth ladder, microprice, and Order Flow Imbalance (OFI).
11. **Options Laboratory (`/options`)**: Analytical Black-Scholes, exact Greeks (Delta, Gamma, Vega, Theta, Rho), Put-Call Parity validation, CRR Binomial Tree, and multi-leg payoffs.
12. **AI Research Copilot (`/copilot`)**: Workspace-grounded quantitative reasoning, methodology pitfall audits, and hypothesis reviews.
13. **Simulated Paper Trading (`/paper-trading`)**: Virtual brokerage account, pre-trade risk controls ($50k notional cap, cash checks), order execution simulation, and kill switch.
14. **Research Tearsheets (`/reports`)**: Institutional performance tearsheets, Markdown research report export, and SHA-256 cryptographic lineage export.
15. **Background Task Telemetry (`/jobs`)**: Task queue monitor, process CPU/memory metrics (psutil), and cancellation controls.

---

## Repository Layout

```text
QuantLab/
├── AGENTS.md                       # Authoritative AI coding agent directives & mandates
├── docs/                           # 17 canonical architecture & planning specifications
│   ├── prd.md                      # Product Requirements Document (18 modules)
│   ├── architecture.md             # System architecture & Mermaid diagrams
│   ├── rules.md                    # Coding invariants & mathematical standards
│   ├── design.md                   # Workstation design system & color tokens
│   ├── tasks.md                    # 64-task implementation backlog & status
│   ├── memory.md                   # Persistent project memory & verification log
│   ├── product_strategy.md         # Competitive analysis & positioning
│   ├── data_sources.md             # Market data ingestion architecture
│   ├── api_contracts.md            # REST API schemas & endpoint contracts
│   ├── database_schema.md          # SQLAlchemy relational models & tables
│   ├── testing_strategy.md         # Testing layers & invariant definitions
│   ├── deployment.md               # Production deployment & operations guide
│   ├── security.md                 # Threat model, RBAC, & worker isolation
│   └── decisions/                  # Architecture Decision Records (ADRs 001-003)
├── backend/                        # FastAPI / Python Quantitative Engine
│   ├── app/
│   │   ├── api/                    # 17 REST API routers
│   │   ├── core/                   # Security, JWT tokens, config, dependency injection
│   │   ├── db/                     # SQLAlchemy 2.0 ORM models & session factory
│   │   ├── schemas/                # Pydantic request/response validation schemas
│   │   ├── services/               # Data, Backtest, ML, Portfolio, & Job services
│   │   ├── copilot/                # Grounded AI context assembler & methodology auditor
│   │   └── engine/                 # Core quantitative computation engine
│   │       ├── backtest/           # Event-driven & vectorized backtesters
│   │       ├── data/               # Merton Jump-Diffusion & 5-point QA auditor
│   │       ├── ml/                 # Zero-leakage features, scalers, & drift tests
│   │       ├── microstructure/     # LimitOrderBook & Poisson stochastic simulator
│   │       ├── options/            # Black-Scholes, CRR Tree, Greeks, & Payoffs
│   │       ├── portfolio/          # Ledoit-Wolf shrinkage, optimizers, & Euler risk
│   │       └── statistics/         # Deflated Sharpe Ratio & Purged K-Fold Walk-Forward
│   ├── tests/
│   │   ├── integration/            # 13-step End-to-End research lifecycle test
│   │   └── unit/                   # 44 domain & quantitative invariant tests
│   ├── requirements.txt            # Python dependencies
│   └── main.py                     # Backend entrypoint
├── frontend/                       # Next.js 14 App Router Workstation UI
│   ├── src/
│   │   ├── app/                    # 17 workstation routes & pages
│   │   ├── components/             # Institutional Shell, Sidebar, Header, UI widgets
│   │   └── lib/                    # API client, Zustand stores, & mathematical utilities
│   ├── package.json                # Frontend dependencies
│   ├── tailwind.config.ts          # Institutional dark workstation design tokens
│   └── tsconfig.json               # TypeScript configuration
└── data/                           # Columnar Apache Parquet storage cache
```

---

## End-to-End Research Lifecycle

QuantLab supports a 13-step research workflow verified via automated testing:

1. **User Authentication**: Secure JWT registration, password hashing (`bcrypt`), and workspace scoping.
2. **Hypothesis Formulation**: Formulate economic mechanism, predicted outcome, and explicit falsification thresholds.
3. **Data Ingestion**: Generate Merton Jump-Diffusion synthetic series or ingest external feeds; run 5-point QA audit.
4. **Exploratory Analytics**: Inspect returns, 4 statistical moments, Jarque-Bera normality, and ADF stationarity.
5. **Strategy Modeling**: Configure entry/exit logic (e.g., Moving Average Crossover, Momentum, Mean Reversion).
6. **Event-Driven Backtest**: Execute with strict $t \to t+1$ open prices, slippage, and fee deductions.
7. **Lineage Fingerprinting**: Generate SHA-256 cryptographic hash binding configuration, data version, and code.
8. **Statistical Validation**: Calculate Deflated Sharpe Ratio ($SR^*$) to penalize selection bias across trials.
9. **Machine Learning Pipeline**: Compute technical features, perform chronological train-only scaling, and test for KS drift.
10. **Portfolio Allocation**: Solve for Max Sharpe or Equal Risk Parity with Ledoit-Wolf shrinkage and verify Euler decomposition.
11. **Microstructure Simulation**: Validate fill probability and queue dynamics in the double-auction LOB simulator.
12. **Derivatives Analysis**: Compute options fair value, Black-Scholes Greeks, Put-Call Parity, and multi-leg payoffs.
13. **Institutional Reporting**: Export full Markdown research tearsheet and cryptographic JSON lineage bundle.

---

## REST API Specifications

The backend exposes a fully typed REST API with interactive Swagger docs at `http://localhost:8000/docs`:

| Route Prefix | Endpoints | Description |
| :--- | :--- | :--- |
| `/api/v1/auth` | `POST /register`, `POST /login` | JWT authentication and session token issuance |
| `/api/v1/projects` | `GET /`, `POST /`, `POST /{id}/hypotheses` | Research project and hypothesis management |
| `/api/v1/datasets` | `POST /generate-synthetic`, `GET /` | Merton Jump-Diffusion generator & QA audit |
| `/api/v1/analytics` | `POST /summary` | Moments, Jarque-Bera, ADF test, and ACF lags |
| `/api/v1/backtests` | `POST /run`, `GET /{id}` | Event-driven backtester with $t \to t+1$ semantics |
| `/api/v1/validation`| `POST /deflated-sharpe`, `POST /walk-forward` | Deflated Sharpe Ratio and Purged K-Fold validation |
| `/api/v1/ml` | `POST /train`, `GET /features` | Supervised financial ML and Kolmogorov-Smirnov drift |
| `/api/v1/portfolio` | `POST /optimize` | Ledoit-Wolf covariance, Max Sharpe, and Euler risk |
| `/api/v1/microstructure` | `POST /simulate`, `POST /order` | Double-auction LOB simulator & tape inspection |
| `/api/v1/options` | `POST /price`, `POST /implied-vol`, `POST /payoff` | Black-Scholes, CRR Tree, Greeks, and Payoffs |
| `/api/v1/copilot` | `POST /chat`, `POST /audit-methodology` | Context-grounded AI copilot & methodology auditor |
| `/api/v1/paper-trading` | `GET /account`, `POST /orders`, `POST /kill-switch` | Simulated paper brokerage & pre-trade risk controls |
| `/api/v1/reports` | `GET /experiments/{id}/tearsheet`, `.../export/markdown` | Research tearsheets & Markdown/JSON exports |
| `/api/v1/jobs` | `GET /`, `POST /{id}/cancel`, `GET /telemetry` | Background task queue & process telemetry |

---

## Getting Started & Quickstart

### Prerequisites

- **Python**: 3.11+ (Python 3.13 tested and verified)
- **Node.js**: v18+ (Node.js v26 tested and verified)
- **Git**

### Backend Setup (FastAPI & Python 3.13)

```powershell
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start FastAPI development server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- API server runs at: `http://localhost:8000`
- Interactive OpenAPI Swagger documentation: `http://localhost:8000/docs`

### Frontend Setup (Next.js 14 & Tailwind CSS)

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```

- Quantitative Workstation interface: `http://localhost:3000`

---

## Automated Verification & Test Suite

QuantLab includes an automated test suite verifying both software functionality and mathematical correctness:

```powershell
# Run the entire backend test suite
cd backend
python -m pytest tests -v
```

### Test Suite Execution Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-8.3.4
collected 45 items

tests/integration/test_e2e_research_lifecycle.py::test_full_quantitative_research_lifecycle PASSED [  2%]
tests/unit/test_auth.py::test_auth_registration_and_login PASSED         [  4%]
tests/unit/test_backtest.py::test_strategy_signal_generation PASSED      [  6%]
tests/unit/test_backtest.py::test_event_backtester_cash_conservation_and_costs PASSED [  8%]
tests/unit/test_backtest.py::test_no_lookahead_bias_invariant PASSED     [ 11%]
tests/unit/test_backtest.py::test_backtest_api_execution_and_lineage PASSED [ 13%]
tests/unit/test_copilot.py::test_methodology_auditor_pitfalls PASSED     [ 15%]
tests/unit/test_copilot.py::test_copilot_grounded_evidence_extraction PASSED [ 17%]
tests/unit/test_copilot.py::test_copilot_api_endpoints PASSED            [ 20%]
tests/unit/test_datasets.py::test_synthetic_data_generator_deterministic_and_invariants PASSED [ 22%]
tests/unit/test_datasets.py::test_data_quality_audit PASSED              [ 24%]
tests/unit/test_datasets.py::test_datasets_api_lifecycle PASSED          [ 26%]
tests/unit/test_eda.py::test_eda_returns_and_volatility PASSED           [ 28%]
tests/unit/test_eda.py::test_eda_distribution_and_drawdown PASSED        [ 31%]
tests/unit/test_eda.py::test_analytics_api_endpoint PASSED               [ 33%]
tests/unit/test_health.py::test_health_check PASSED                      [ 35%]
tests/unit/test_health.py::test_root_endpoint PASSED                     [ 37%]
tests/unit/test_jobs.py::test_jobs_and_telemetry_lifecycle PASSED        [ 40%]
tests/unit/test_microstructure.py::test_lob_price_time_priority PASSED   [ 42%]
tests/unit/test_microstructure.py::test_lob_crossing_execution PASSED    [ 44%]
tests/unit/test_microstructure.py::test_lob_microprice_and_ofi PASSED    [ 46%]
tests/unit/test_microstructure.py::test_lob_cancellation PASSED          [ 48%]
tests/unit/test_microstructure.py::test_microstructure_simulator_and_api PASSED [ 51%]
tests/unit/test_ml.py::test_build_financial_features PASSED              [ 53%]
tests/unit/test_ml.py::test_zero_leakage_scaling_invariant PASSED        [ 55%]
tests/unit/test_ml.py::test_train_models_and_drift PASSED                [ 57%]
tests/unit/test_ml.py::test_ml_api_endpoints PASSED                      [ 60%]
tests/unit/test_options.py::test_black_scholes_pricing_and_put_call_parity PASSED [ 62%]
tests/unit/test_options.py::test_black_scholes_greeks_invariants PASSED  [ 64%]
tests/unit/test_options.py::test_binomial_tree_convergence PASSED        [ 66%]
tests/unit/test_options.py::test_implied_volatility_inversion PASSED     [ 68%]
tests/unit/test_options.py::test_options_strategy_payoffs PASSED         [ 71%]
tests/unit/test_options.py::test_options_api_endpoints PASSED            [ 73%]
tests/unit/test_paper_trading.py::test_paper_trading_lifecycle PASSED    [ 75%]
tests/unit/test_portfolio.py::test_covariance_and_ledoit_wolf_shrinkage PASSED [ 77%]
tests/unit/test_portfolio.py::test_marginal_risk_contribution_invariant PASSED [ 80%]
tests/unit/test_portfolio.py::test_portfolio_optimizers_mathematical_properties PASSED [ 82%]
tests/unit/test_portfolio.py::test_portfolio_api_endpoint PASSED         [ 84%]
tests/unit/test_projects.py::test_research_project_and_hypothesis_lifecycle PASSED [ 86%]
tests/unit/test_projects.py::test_project_cross_tenant_isolation PASSED  [ 88%]
tests/unit/test_rbac.py::test_multi_tenant_workspace_isolation PASSED    [ 91%]
tests/unit/test_reports.py::test_reports_api_and_markdown_export PASSED  [ 93%]
tests/unit/test_validation.py::test_purged_kfold_no_overlap_and_embargo PASSED [ 95%]
tests/unit/test_validation.py::test_deflated_sharpe_ratio_multiple_testing_penalty PASSED [ 97%]
tests/unit/test_validation.py::test_validation_api_endpoints PASSED      [100%]

======================== 45 passed in 8.16s ========================
```

### Production Build Verification (Frontend):
```powershell
cd frontend
npm run build
# Verified: 17 static and dynamic routes compiled and pre-rendered cleanly with 0 errors
```

---

## Canonical Documentation Suite

All system specifications and architecture decision records are available in the [`docs/`](docs/) directory:

- **[AGENTS.md](AGENTS.md)**: AI coding directives & mandates.
- **[docs/prd.md](docs/prd.md)**: Complete product requirements document.
- **[docs/architecture.md](docs/architecture.md)**: Full system architecture with 10 Mermaid flowcharts.
- **[docs/rules.md](docs/rules.md)**: Engineering standards & mathematical invariant constraints.
- **[docs/design.md](docs/design.md)**: Design system tokens & page specifications.
- **[docs/tasks.md](docs/tasks.md)**: 64-task implementation backlog with live status.
- **[docs/memory.md](docs/memory.md)**: Persistent project memory & verification log.
- **[docs/decisions/](docs/decisions/)**: Architecture Decision Records (ADRs 001–003).

---

## License & Acknowledgments

This project is licensed under the **MIT License**.

Built for quantitative researchers, algorithmic traders, data scientists, and students dedicated to mathematical rigor and reproducibility in financial markets.
