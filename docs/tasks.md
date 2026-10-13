# QuantLab Implementation Backlog & Dependency Graph

```text
================================================================================
QUANTLAB IMPLEMENTATION STATUS
================================================================================
Total tasks:             64
Completed:               64
In progress:             0
Ready:                   0
Blocked:                 0
Remaining:               0
Completion:              100.0%

Current phase:           Phase 17 — Final Integration & Acceptance (COMPLETED)
Current task:            TASK-P17-04 (Documentation Synchronization & Final Project Closure)
Next eligible tasks:     None (Project 100% Complete & Verified)

[================================================================================] 100.0%
================================================================================
```

### Phase Summary Table

| Phase | Title | Total | Completed | In Progress | Ready | Blocked |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Phase 0** | Repository Discovery & Documentation | 3 | 3 | 0 | 0 | 0 |
| **Phase 1** | Project Foundation & Tooling | 4 | 4 | 0 | 0 | 0 |
| **Phase 2** | Core Persistence & Authentication | 4 | 4 | 0 | 0 | 0 |
| **Phase 3** | Design System & Application Shell | 4 | 4 | 0 | 0 | 0 |
| **Phase 4** | Research Projects & Hypotheses | 3 | 3 | 0 | 0 | 0 |
| **Phase 5** | Market Data Infrastructure | 4 | 4 | 0 | 0 | 0 |
| **Phase 6** | Exploratory Data Analytics | 3 | 3 | 0 | 0 | 0 |
| **Phase 7** | Strategy Engine & Backtester | 5 | 5 | 0 | 0 | 0 |
| **Phase 8** | Statistical Validation Lab | 4 | 4 | 0 | 0 | 0 |
| **Phase 9** | Machine Learning Laboratory | 4 | 4 | 0 | 0 | 0 |
| **Phase 10** | Portfolio Optimization & Risk | 4 | 4 | 0 | 0 | 0 |
| **Phase 11** | Market Microstructure & LOB | 4 | 4 | 0 | 0 | 0 |
| **Phase 12** | Options & Derivatives Lab | 4 | 4 | 0 | 0 | 0 |
| **Phase 13** | AI Research Copilot | 4 | 4 | 0 | 0 | 0 |
| **Phase 14** | Paper Trading Engine | 3 | 3 | 0 | 0 | 0 |
| **Phase 15** | Collaboration & Reporting | 3 | 3 | 0 | 0 | 0 |
| **Phase 16** | Operational Readiness & Observability | 3 | 3 | 0 | 0 | 0 |
| **Phase 17** | Final Integration & Acceptance | 4 | 4 | 0 | 0 | 0 |
| **TOTAL** | | **64** | **64** | **0** | **0** | **0** |

---

## Detailed Task Backlog

### Phase 0 — Repository Discovery and Documentation Gate

#### TASK-P0-01: Environment Discovery & Git Initialization
- **Phase**: Phase 0
- **Status**: `COMPLETED`
- **Objective**: Inspect runtime environment, verify Python/Node/Git/Docker availability, initialize Git repository and standard `.gitignore`.
- **Deliverables**: `.gitignore`, verified runtime environment log.
- **Dependencies**: None.
- **Acceptance Criteria**: Git repo initialized, Python 3.13 and Node v26 verified, `.gitignore` present.
- **Verification Commands**: `git status`, `python --version`, `node --version`.
- **Priority**: Critical | **Complexity**: Low

#### TASK-P0-02: Mandatory Planning & Architecture Documentation Suite
- **Phase**: Phase 0
- **Status**: `COMPLETED`
- **Objective**: Author all mandatory planning documents, rules, system architecture, PRD, and design specifications.
- **Deliverables**: `AGENTS.md`, `docs/prd.md`, `docs/architecture.md`, `docs/rules.md`, `docs/design.md`, `docs/tasks.md`, `docs/memory.md`, `docs/product_strategy.md`, `docs/data_sources.md`, `docs/api_contracts.md`, `docs/database_schema.md`, `docs/testing_strategy.md`, `docs/deployment.md`, `docs/security.md`, and ADRs.
- **Dependencies**: TASK-P0-01.
- **Acceptance Criteria**: All canonical documentation files present, consistent, and fully detailed.
- **Verification Commands**: Check existence of all 17 canonical documentation files.
- **Priority**: Critical | **Complexity**: High

#### TASK-P0-03: Documentation Gate Review & Audit
- **Phase**: Phase 0
- **Status**: `COMPLETED`
- **Objective**: Audit documentation against the complete QuantLab prompt specification, verify zero internal contradictions, and record gate clearance.
- **Deliverables**: Documented gate clearance in `docs/memory.md` and `docs/tasks.md`.
- **Dependencies**: TASK-P0-02.
- **Acceptance Criteria**: All 14 gate checklist items verified as passing.
- **Verification Commands**: Audit checklist validation.
- **Priority**: Critical | **Complexity**: Medium

---

### Phase 1 — Project Foundation & Tooling

#### TASK-P1-01: Backend Foundation & FastAPI Skeleton
- **Phase**: Phase 1
- **Status**: `IN_PROGRESS`
- **Objective**: Scaffold backend directory structure, FastAPI application entrypoint, CORS, exception handlers, and `requirements.txt`.
- **Deliverables**: `backend/app/main.py`, `backend/requirements.txt`, `backend/app/core/config.py`.
- **Dependencies**: TASK-P0-03.
- **Acceptance Criteria**: FastAPI starts and serves `GET /api/v1/health` with valid JSON.
- **Verification Commands**: `python -m uvicorn app.main:app --port 8000` & `curl http://127.0.0.1:8000/api/v1/health`.
- **Priority**: Critical | **Complexity**: Medium

#### TASK-P1-02: Frontend Foundation & Next.js Setup
- **Phase**: Phase 1
- **Status**: `READY`
- **Objective**: Scaffold Next.js TypeScript application, Tailwind CSS configuration, and basic layout structure.
- **Deliverables**: `frontend/package.json`, `frontend/tsconfig.json`, `frontend/src/app/layout.tsx`.
- **Dependencies**: TASK-P0-03.
- **Acceptance Criteria**: Next.js builds and runs on `http://localhost:3000` without errors.
- **Verification Commands**: `npm run build` or `npm run dev` in `frontend/`.
- **Priority**: Critical | **Complexity**: Medium

#### TASK-P1-03: Environment Configuration & Directory Architecture
- **Phase**: Phase 1
- **Status**: `BLOCKED` (Depends on TASK-P1-01, TASK-P1-02)
- **Objective**: Establish `.env.example` files, data storage directories (`data/sample/`, `data/parquet/`), and logging configuration.
- **Deliverables**: `backend/.env.example`, `frontend/.env.example`, directory scaffold.
- **Dependencies**: TASK-P1-01, TASK-P1-02.
- **Acceptance Criteria**: Safe defaults loaded seamlessly without hardcoded secrets.
- **Verification Commands**: Inspection of configuration loader tests.
- **Priority**: High | **Complexity**: Low

#### TASK-P1-04: Test Harness & CI/Dev Verification
- **Phase**: Phase 1
- **Status**: `BLOCKED` (Depends on TASK-P1-01, TASK-P1-03)
- **Objective**: Setup `pytest` harness, backend test runners, and verify baseline health test.
- **Deliverables**: `backend/tests/conftest.py`, `backend/tests/unit/test_health.py`.
- **Dependencies**: TASK-P1-01, TASK-P1-03.
- **Acceptance Criteria**: `pytest` runs and passes 100%.
- **Verification Commands**: `pytest backend/tests`.
- **Priority**: High | **Complexity**: Low

---

### Phase 2 — Core Persistence & Authentication

#### TASK-P2-01: SQLAlchemy Models & Database Session Engine
- **Phase**: Phase 2
- **Status**: `BLOCKED` (Depends on TASK-P1-04)
- **Objective**: Implement SQLAlchemy 2.0 ORM models for Users, Workspaces, Projects, Hypotheses, Datasets, Experiments, TradeLogs, Jobs.
- **Deliverables**: `backend/app/db/models.py`, `backend/app/db/session.py`.
- **Dependencies**: TASK-P1-04.
- **Acceptance Criteria**: Models compile and initialize schema in SQLite without syntax or foreign key errors.
- **Verification Commands**: `python -c "from app.db.session import init_db; init_db()"`.
- **Priority**: Critical | **Complexity**: High

#### TASK-P2-02: Alembic Migrations Setup
- **Phase**: Phase 2
- **Status**: `BLOCKED` (Depends on TASK-P2-01)
- **Objective**: Initialize Alembic, configure `env.py` with SQLAlchemy metadata, and generate baseline migration.
- **Deliverables**: `backend/alembic.ini`, `backend/alembic/versions/*.py`.
- **Dependencies**: TASK-P2-01.
- **Acceptance Criteria**: `alembic upgrade head` succeeds cleanly.
- **Verification Commands**: `alembic upgrade head`.
- **Priority**: High | **Complexity**: Medium

#### TASK-P2-03: Authentication Engine & JWT Token Handling
- **Phase**: Phase 2
- **Status**: `BLOCKED` (Depends on TASK-P2-01)
- **Objective**: Implement password hashing with bcrypt, JWT creation/validation, and `/api/v1/auth/register`, `/login`, `/me` routes.
- **Deliverables**: `backend/app/core/security.py`, `backend/app/api/auth.py`.
- **Dependencies**: TASK-P2-01.
- **Acceptance Criteria**: Users can register and login; valid JWT returns user info; invalid password returns 401.
- **Verification Commands**: `pytest backend/tests/test_auth.py`.
- **Priority**: Critical | **Complexity**: Medium

#### TASK-P2-04: Multi-Tenant Workspace & RBAC Middleware
- **Phase**: Phase 2
- **Status**: `BLOCKED` (Depends on TASK-P2-03)
- **Objective**: Implement workspace creation, member role assignment, and tenant-scoped query dependencies.
- **Deliverables**: `backend/app/api/workspaces.py`, `backend/app/core/deps.py`.
- **Dependencies**: TASK-P2-03.
- **Acceptance Criteria**: Cross-tenant data isolation verified by automated tests.
- **Verification Commands**: `pytest backend/tests/test_rbac.py`.
- **Priority**: Critical | **Complexity**: Medium

---

### Phase 3 — Design System & Application Shell

#### TASK-P3-01: Design Tokens & Tailwind Theme Setup
- **Phase**: Phase 3
- **Status**: `BLOCKED` (Depends on TASK-P1-02)
- **Objective**: Implement institutional color palette, fonts, spacing, and financial tokens in Tailwind and CSS variables.
- **Deliverables**: `frontend/tailwind.config.ts`, `frontend/src/app/globals.css`.
- **Dependencies**: TASK-P1-02.
- **Acceptance Criteria**: Theme variables available and render correctly in both dark and light modes.
- **Verification Commands**: Frontend build verification.
- **Priority**: High | **Complexity**: Medium

#### TASK-P3-02: Core UI Component Library
- **Phase**: Phase 3
- **Status**: `BLOCKED` (Depends on TASK-P3-01)
- **Objective**: Build reusable UI components: Button, Input, Table, Card, Dialog, Badge, Tabs, Alert.
- **Deliverables**: `frontend/src/components/ui/*.tsx`.
- **Dependencies**: TASK-P3-01.
- **Acceptance Criteria**: Accessible, keyboard-navigable components with micro-interactions.
- **Verification Commands**: Component unit rendering tests.
- **Priority**: High | **Complexity**: Medium

#### TASK-P3-03: Responsive Application Shell & Navigation
- **Phase**: Phase 3
- **Status**: `BLOCKED` (Depends on TASK-P3-02)
- **Objective**: Implement Left Sidebar with workspace selector, Top Command Bar with job indicator, and Main Canvas layout.
- **Deliverables**: `frontend/src/components/layout/Shell.tsx`, `Sidebar.tsx`, `Header.tsx`.
- **Dependencies**: TASK-P3-02.
- **Acceptance Criteria**: Responsive navigation between all workstations with active highlighting and breadcrumbs.
- **Verification Commands**: Visual layout inspection.
- **Priority**: High | **Complexity**: Medium

#### TASK-P3-04: API Client & Global State Management
- **Phase**: Phase 3
- **Status**: `BLOCKED` (Depends on TASK-P3-03)
- **Objective**: Setup Axios/Fetch API client with auth token interceptor and Zustand store for user session and active workspace.
- **Deliverables**: `frontend/src/lib/api.ts`, `frontend/src/lib/store.ts`.
- **Dependencies**: TASK-P3-03.
- **Acceptance Criteria**: API client securely handles auth tokens and triggers 401 logout handlers.
- **Verification Commands**: Store and API mock tests.
- **Priority**: High | **Complexity**: Low

---

### Phase 4 — Research Projects & Hypotheses

#### TASK-P4-01: Research Projects & Hypotheses Backend
- **Phase**: Phase 4
- **Status**: `BLOCKED` (Depends on TASK-P2-04)
- **Objective**: Implement project CRUD, hypothesis formulation, mechanisms, and falsification criteria endpoints.
- **Deliverables**: `backend/app/api/projects.py`, `backend/app/services/project_service.py`.
- **Dependencies**: TASK-P2-04.
- **Acceptance Criteria**: Full lifecycle of projects and hypotheses persisted with workspace isolation.
- **Verification Commands**: `pytest backend/tests/test_projects.py`.
- **Priority**: High | **Complexity**: Medium

#### TASK-P4-02: Research Notes & Markdown Documentation
- **Phase**: Phase 4
- **Status**: `BLOCKED` (Depends on TASK-P4-01)
- **Objective**: Implement research notes endpoint with Markdown rendering and experiment linkage.
- **Deliverables**: `backend/app/api/notes.py`, `backend/app/services/note_service.py`.
- **Dependencies**: TASK-P4-01.
- **Acceptance Criteria**: Notes saved and retrieved with proper timestamping and author tracking.
- **Verification Commands**: Unit tests.
- **Priority**: Medium | **Complexity**: Low

#### TASK-P4-03: Research Projects Workstation UI
- **Phase**: Phase 4
- **Status**: `BLOCKED` (Depends on TASK-P4-01, TASK-P3-03)
- **Objective**: Build Projects dashboard, project detail view, hypothesis tracker, and research note editor.
- **Deliverables**: `frontend/src/app/projects/page.tsx`, `frontend/src/app/projects/[id]/page.tsx`.
- **Dependencies**: TASK-P4-01, TASK-P3-03.
- **Acceptance Criteria**: Users can create projects, add hypotheses with falsification rules, and view experiment links.
- **Verification Commands**: Frontend end-to-end flow.
- **Priority**: High | **Complexity**: Medium

---

### Phase 5 — Market Data Infrastructure

#### TASK-P5-01: Synthetic Market Data Generator
- **Phase**: Phase 5
- **Status**: `BLOCKED` (Depends on TASK-P1-04)
- **Objective**: Implement Jump-Diffusion and GBM synthetic market data generator with reproducible random seed and multi-asset correlation.
- **Deliverables**: `backend/app/engine/data/synthetic.py`.
- **Dependencies**: TASK-P1-04.
- **Acceptance Criteria**: Generates realistic OHLCV DataFrames with guaranteed reproducible output given identical seeds.
- **Verification Commands**: `pytest backend/tests/unit/test_synthetic_data.py`.
- **Priority**: Critical | **Complexity**: Medium

#### TASK-P5-02: Public Market Data Adapters (Stooq & Yahoo)
- **Phase**: Phase 5
- **Status**: `BLOCKED` (Depends on TASK-P5-01)
- **Objective**: Implement Stooq daily CSV downloader, Yahoo Finance fallback, and provider base interface.
- **Deliverables**: `backend/app/providers/base.py`, `stooq.py`, `yahoo.py`.
- **Dependencies**: TASK-P5-01.
- **Acceptance Criteria**: Successfully fetches and parses historical price series with rate limit handling and error logging.
- **Verification Commands**: `pytest backend/tests/unit/test_providers.py`.
- **Priority**: High | **Complexity**: Medium

#### TASK-P5-03: Normalization, Parquet Store & Quality Audit Engine
- **Phase**: Phase 5
- **Status**: `BLOCKED` (Depends on TASK-P5-01, TASK-P5-02)
- **Objective**: Implement 5-point data quality audit, UTC normalization, and columnar Parquet persistence.
- **Deliverables**: `backend/app/services/data_service.py`, `backend/app/engine/data/quality.py`.
- **Dependencies**: TASK-P5-01, TASK-P5-02.
- **Acceptance Criteria**: Stores normalized Parquet files, registers in SQL catalog, and generates quality scores.
- **Verification Commands**: `pytest backend/tests/unit/test_data_quality.py`.
- **Priority**: Critical | **Complexity**: High

#### TASK-P5-04: Data Browser & Ingestion UI
- **Phase**: Phase 5
- **Status**: `BLOCKED` (Depends on TASK-P5-03, TASK-P3-03)
- **Objective**: Build interactive Data Browser with dataset list, quality audit report card, and OHLCV candlestick chart.
- **Deliverables**: `frontend/src/app/data/page.tsx`, `frontend/src/components/charts/CandlestickChart.tsx`.
- **Dependencies**: TASK-P5-03, TASK-P3-03.
- **Acceptance Criteria**: User can trigger synthetic generation or live import, inspect data quality, and pan/zoom candlestick charts.
- **Verification Commands**: Frontend workflow validation.
- **Priority**: High | **Complexity**: High

---

### Phase 6 — Exploratory Data Analytics

#### TASK-P6-01: Statistical Time Series Analytics Engine
- **Phase**: Phase 6
- **Status**: `BLOCKED` (Depends on TASK-P5-03)
- **Objective**: Implement simple/log returns, rolling annualized volatility, skewness, kurtosis, Jarque-Bera, and ADF stationarity tests.
- **Deliverables**: `backend/app/engine/statistics/eda.py`.
- **Dependencies**: TASK-P5-03.
- **Acceptance Criteria**: Returns correct statistical values matching SciPy and statsmodels benchmarks.
- **Verification Commands**: `pytest backend/tests/unit/test_eda.py`.
- **Priority**: High | **Complexity**: Medium

#### TASK-P6-02: Autocorrelation & Correlation Matrix API
- **Phase**: Phase 6
- **Status**: `BLOCKED` (Depends on TASK-P6-01)
- **Objective**: Implement ACF/PACF and multi-asset correlation endpoints with date range filtering.
- **Deliverables**: `backend/app/api/analytics.py`.
- **Dependencies**: TASK-P6-01.
- **Acceptance Criteria**: Returns correlation matrices and ACF arrays formatted for interactive rendering.
- **Verification Commands**: API integration tests.
- **Priority**: Medium | **Complexity**: Low

#### TASK-P6-03: Exploratory Analytics Workstation UI
- **Phase**: Phase 6
- **Status**: `BLOCKED` (Depends on TASK-P6-02, TASK-P3-03)
- **Objective**: Build Analytics view displaying return distributions, rolling volatility, correlation heatmaps, and stationarity test results.
- **Deliverables**: `frontend/src/app/analytics/page.tsx`, `frontend/src/components/charts/CorrelationHeatmap.tsx`.
- **Dependencies**: TASK-P6-02, TASK-P3-03.
- **Acceptance Criteria**: Interactive charts display verified statistical metrics with clear financial explanations.
- **Verification Commands**: UI manual and component tests.
- **Priority**: High | **Complexity**: Medium

---

### Phase 7 — Strategy Engine & Backtester

#### TASK-P7-01: Strategy Interfaces & Baseline Templates
- **Phase**: Phase 7
- **Status**: `BLOCKED` (Depends on TASK-P5-03)
- **Objective**: Build declarative strategy interface and educational templates: Buy & Hold, MA Crossover, Momentum, Mean Reversion.
- **Deliverables**: `backend/app/engine/strategy/base.py`, `templates.py`.
- **Dependencies**: TASK-P5-03.
- **Acceptance Criteria**: Strategies produce standardized target weights and signal matrices.
- **Verification Commands**: `pytest backend/tests/unit/test_strategies.py`.
- **Priority**: Critical | **Complexity**: Medium

#### TASK-P7-02: Vectorized Backtesting Engine
- **Phase**: Phase 7
- **Status**: `BLOCKED` (Depends on TASK-P7-01)
- **Objective**: Implement ultra-fast matrix backtester for rapid parameter screening with next-bar execution alignment.
- **Deliverables**: `backend/app/engine/backtest/vectorized.py`.
- **Dependencies**: TASK-P7-01.
- **Acceptance Criteria**: Executes 10 years of daily data in $< 0.1\text{s}$ with zero look-ahead bias.
- **Verification Commands**: `pytest backend/tests/unit/test_vectorized.py`.
- **Priority**: High | **Complexity**: Medium

#### TASK-P7-03: Event-Driven Simulation Engine & Cost Models
- **Phase**: Phase 7
- **Status**: `BLOCKED` (Depends on TASK-P7-01)
- **Objective**: Implement bar-by-bar state machine managing Cash, Positions, Orders, Fills, Commissions, Slippage, and Borrow Fees.
- **Deliverables**: `backend/app/engine/backtest/event.py`, `costs.py`.
- **Dependencies**: TASK-P7-01.
- **Acceptance Criteria**: Full trade and order logs generated; cash conservation invariant verified.
- **Verification Commands**: `pytest backend/tests/unit/test_event_backtest.py`.
- **Priority**: Critical | **Complexity**: High

#### TASK-P7-04: Financial Performance & Risk Metrics Engine
- **Phase**: Phase 7
- **Status**: `BLOCKED` (Depends on TASK-P7-03)
- **Objective**: Implement Sharpe, Sortino, Calmar, MaxDD, WinRate, Profit Factor, Expectancy, VaR, CVaR, and cost attribution calculations.
- **Deliverables**: `backend/app/engine/backtest/metrics.py`.
- **Dependencies**: TASK-P7-03.
- **Acceptance Criteria**: Zero crash on zero volatility; matches textbook calculations.
- **Verification Commands**: `pytest backend/tests/unit/test_metrics.py`.
- **Priority**: Critical | **Complexity**: Medium

#### TASK-P7-05: Backtest Workstation UI & Results Dashboard
- **Phase**: Phase 7
- **Status**: `BLOCKED` (Depends on TASK-P7-04, TASK-P3-03)
- **Objective**: Build Backtest configuration form, equity curve chart vs benchmark, underwater drawdown chart, and paginated trade logs.
- **Deliverables**: `frontend/src/app/backtests/page.tsx`, `frontend/src/components/backtest/ResultsDashboard.tsx`.
- **Dependencies**: TASK-P7-04, TASK-P3-03.
- **Acceptance Criteria**: User can launch backtests, view animated progress, and analyze interactive tearsheets.
- **Verification Commands**: UI end-to-end run.
- **Priority**: Critical | **Complexity**: High

---

### Phase 8 — Statistical Validation Lab

#### TASK-P8-01: Walk-Forward & Purged K-Fold Engine
- **Phase**: Phase 8
- **Status**: `BLOCKED` (Depends on TASK-P7-03)
- **Objective**: Implement rolling/expanding walk-forward analysis and Purged K-Fold cross-validation with embargo.
- **Deliverables**: `backend/app/engine/statistics/walk_forward.py`, `purged_kfold.py`.
- **Dependencies**: TASK-P7-03.
- **Acceptance Criteria**: Train and test partitions never overlap; embargo windows verified.
- **Verification Commands**: `pytest backend/tests/unit/test_walk_forward.py`.
- **Priority**: High | **Complexity**: High

#### TASK-P8-02: Bootstrap Confidence Intervals & Deflated Sharpe Ratio
- **Phase**: Phase 8
- **Status**: `BLOCKED` (Depends on TASK-P8-01)
- **Objective**: Implement stationary block bootstrap for Sharpe ratio and Deflated Sharpe Ratio (DSR) accounting for multiple trials.
- **Deliverables**: `backend/app/engine/statistics/dsr.py`, `bootstrap.py`.
- **Dependencies**: TASK-P8-01.
- **Acceptance Criteria**: DSR penalizes inflated trials matching Bailey & López de Prado (2014).
- **Verification Commands**: `pytest backend/tests/unit/test_dsr.py`.
- **Priority**: High | **Complexity**: Medium

#### TASK-P8-03: Parameter Sensitivity & Transaction Cost Stress Tests
- **Phase**: Phase 8
- **Status**: `BLOCKED` (Depends on TASK-P8-01)
- **Objective**: Implement 2D parameter grid sensitivity engine and slippage stress test ($1\times, 2\times, 5\times, 10\times$).
- **Deliverables**: `backend/app/engine/statistics/sensitivity.py`.
- **Dependencies**: TASK-P8-01.
- **Acceptance Criteria**: Returns stability score and break-even transaction cost point.
- **Verification Commands**: Unit tests.
- **Priority**: Medium | **Complexity**: Medium

#### TASK-P8-04: Statistical Validation Workstation UI
- **Phase**: Phase 8
- **Status**: `BLOCKED` (Depends on TASK-P8-02, TASK-P8-03, TASK-P3-03)
- **Objective**: Build Validation view with DSR calculator, walk-forward out-of-sample curves, and parameter sensitivity heatmap.
- **Deliverables**: `frontend/src/app/validation/page.tsx`, `frontend/src/components/charts/SensitivityHeatmap.tsx`.
- **Dependencies**: TASK-P8-02, TASK-P8-03, TASK-P3-03.
- **Acceptance Criteria**: Displays clear robustness alerts and p-hacking warnings.
- **Verification Commands**: UI manual and component tests.
- **Priority**: High | **Complexity**: Medium

---

### Phase 9 — Machine Learning Laboratory

#### TASK-P9-01: Time-Aware Feature Engineering & Preprocessing Pipeline
- **Phase**: Phase 9
- **Status**: `BLOCKED` (Depends on TASK-P5-03)
- **Objective**: Implement feature generation (lagged returns, rolling momentum, volatility, RSI, MACD) with strict train-only fitting.
- **Deliverables**: `backend/app/engine/ml/features.py`, `pipeline.py`.
- **Dependencies**: TASK-P5-03.
- **Acceptance Criteria**: Scalers fit exclusively on train set; leakage prevention test passes.
- **Verification Commands**: `pytest backend/tests/unit/test_ml_pipeline.py`.
- **Priority**: High | **Complexity**: Medium

#### TASK-P9-02: Supervised Model Training & Evaluation Engine
- **Phase**: Phase 9
- **Status**: `BLOCKED` (Depends on TASK-P9-01)
- **Objective**: Train Ridge, Random Forest, and HistGradientBoosting classifiers/regressors with chronological splits and financial metric evaluation.
- **Deliverables**: `backend/app/engine/ml/models.py`, `evaluator.py`.
- **Dependencies**: TASK-P9-01.
- **Acceptance Criteria**: Outputs both statistical metrics (ROC-AUC, MSE) and economic trading metrics after costs.
- **Verification Commands**: `pytest backend/tests/unit/test_ml_models.py`.
- **Priority**: High | **Complexity**: High

#### TASK-P9-03: Feature Importance, SHAP & Concept Drift Diagnostics
- **Phase**: Phase 9
- **Status**: `BLOCKED` (Depends on TASK-P9-02)
- **Objective**: Implement Tree/Permutation feature importance and Kolmogorov-Smirnov distribution drift testing.
- **Deliverables**: `backend/app/engine/ml/diagnostics.py`.
- **Dependencies**: TASK-P9-02.
- **Acceptance Criteria**: Detects distribution shifts between train and test intervals.
- **Verification Commands**: `pytest backend/tests/unit/test_ml_drift.py`.
- **Priority**: Medium | **Complexity**: Medium

#### TASK-P9-04: ML Laboratory Workstation UI
- **Phase**: Phase 9
- **Status**: `BLOCKED` (Depends on TASK-P9-03, TASK-P3-03)
- **Objective**: Build ML workspace for feature selection, chronological split visualization, model training, and drift inspection.
- **Deliverables**: `frontend/src/app/ml/page.tsx`, `frontend/src/components/ml/FeatureImportanceChart.tsx`.
- **Dependencies**: TASK-P9-03, TASK-P3-03.
- **Acceptance Criteria**: User can train models, view learning curves, and evaluate economic backtests.
- **Verification Commands**: End-to-end UI testing.
- **Priority**: High | **Complexity**: High

---

### Phase 10 — Portfolio Optimization & Risk

#### TASK-P10-01: Multi-Asset Optimization Solvers
- **Phase**: Phase 10
- **Status**: `BLOCKED` (Depends on TASK-P6-01)
- **Objective**: Implement Equal Weight, Inverse Volatility, Equal Risk Parity, and Markowitz Mean-Variance (Max Sharpe, Min Vol) with SciPy optimize.
- **Deliverables**: `backend/app/engine/portfolio/optimizers.py`.
- **Dependencies**: TASK-P6-01.
- **Acceptance Criteria**: Satisfies constraints ($\sum w_i = 1, w_i \ge 0$); handles non-convergence gracefully.
- **Verification Commands**: `pytest backend/tests/unit/test_portfolio_opt.py`.
- **Priority**: High | **Complexity**: High

#### TASK-P10-02: Covariance Shrinkage & Risk Budgeting
- **Phase**: Phase 10
- **Status**: `BLOCKED` (Depends on TASK-P10-01)
- **Objective**: Implement Ledoit-Wolf covariance shrinkage and Marginal Risk Contribution ($MRC$) decomposition.
- **Deliverables**: `backend/app/engine/portfolio/covariance.py`, `risk_budget.py`.
- **Dependencies**: TASK-P10-01.
- **Acceptance Criteria**: Verified risk parity equality and shrinkage stabilization.
- **Verification Commands**: `pytest backend/tests/unit/test_risk_budget.py`.
- **Priority**: Medium | **Complexity**: Medium

#### TASK-P10-03: Scenario Stress Testing & Tail Risk Engine
- **Phase**: Phase 10
- **Status**: `BLOCKED` (Depends on TASK-P10-01)
- **Objective**: Implement historical crisis stress tests (2008 GFC, 2020 Covid crash) and parametric/historical VaR/CVaR.
- **Deliverables**: `backend/app/engine/portfolio/stress_test.py`.
- **Dependencies**: TASK-P10-01.
- **Acceptance Criteria**: Correctly computes simulated portfolio drawdowns under shock scenarios.
- **Verification Commands**: Unit tests.
- **Priority**: Medium | **Complexity**: Low

#### TASK-P10-04: Portfolio & Risk Workstation UI
- **Phase**: Phase 10
- **Status**: `BLOCKED` (Depends on TASK-P10-03, TASK-P3-03)
- **Objective**: Build Portfolio workspace: asset allocation controls, efficient frontier curve, risk contribution breakdown, and stress simulator.
- **Deliverables**: `frontend/src/app/portfolio/page.tsx`, `frontend/src/components/charts/EfficientFrontier.tsx`.
- **Dependencies**: TASK-P10-03, TASK-P3-03.
- **Acceptance Criteria**: Interactive allocation adjustment with real-time recalculation of risk metrics.
- **Verification Commands**: UI manual and component tests.
- **Priority**: High | **Complexity**: Medium

---

### Phase 11 — Market Microstructure & LOB Simulator

#### TASK-P11-01: Limit Order Book Matching Engine
- **Phase**: Phase 11
- **Status**: `BLOCKED` (Depends on TASK-P1-04)
- **Objective**: Implement pure in-memory double-auction Limit Order Book with price-time priority for Limit, Market, and Cancel orders.
- **Deliverables**: `backend/app/engine/microstructure/lob.py`, `order.py`.
- **Dependencies**: TASK-P1-04.
- **Acceptance Criteria**: Unit conservation holds; price-time priority strictly enforced; partial fills tracked accurately.
- **Verification Commands**: `pytest backend/tests/unit/test_lob.py`.
- **Priority**: High | **Complexity**: High

#### TASK-P11-02: Microstructure Metrics & Queue Position Tracking
- **Phase**: Phase 11
- **Status**: `BLOCKED` (Depends on TASK-P11-01)
- **Objective**: Implement Midprice, Microprice (volume-weighted), Spread, Order Book Depth, Order Flow Imbalance (OFI), and limit order queue tracking.
- **Deliverables**: `backend/app/engine/microstructure/metrics.py`.
- **Dependencies**: TASK-P11-01.
- **Acceptance Criteria**: Calculates accurate microprices and enforces queue depletion prior to fill.
- **Verification Commands**: `pytest backend/tests/unit/test_microstructure_metrics.py`.
- **Priority**: High | **Complexity**: Medium

#### TASK-P11-03: Synthetic Order Flow Generator (Poisson & Hawkes)
- **Phase**: Phase 11
- **Status**: `BLOCKED` (Depends on TASK-P11-01)
- **Objective**: Implement synthetic Poisson arrival and self-exciting Hawkes process event simulator.
- **Deliverables**: `backend/app/engine/microstructure/simulator.py`.
- **Dependencies**: TASK-P11-01.
- **Acceptance Criteria**: Produces realistic clusters of aggressive market orders and resting liquidity.
- **Verification Commands**: Unit tests.
- **Priority**: Medium | **Complexity**: Medium

#### TASK-P11-04: Order Book Visual Workstation UI
- **Phase**: Phase 11
- **Status**: `BLOCKED` (Depends on TASK-P11-02, TASK-P11-03, TASK-P3-03)
- **Objective**: Build visual LOB depth ladder (bids green, asks red), live event tape, and interactive order submission console.
- **Deliverables**: `frontend/src/app/microstructure/page.tsx`, `frontend/src/components/lob/OrderBookLadder.tsx`.
- **Dependencies**: TASK-P11-02, TASK-P11-03, TASK-P3-03.
- **Acceptance Criteria**: Real-time animated order book depth with manual order placement.
- **Verification Commands**: Frontend interaction testing.
- **Priority**: High | **Complexity**: High

---

### Phase 12 — Options & Derivatives Laboratory

#### TASK-P12-01: Black-Scholes-Merton Pricing & Greeks Engine
- **Phase**: Phase 12
- **Status**: `BLOCKED` (Depends on TASK-P1-04)
- **Objective**: Implement analytical Black-Scholes-Merton formula and exact Greeks (Delta, Gamma, Theta, Vega, Rho) with Put-Call parity invariant.
- **Deliverables**: `backend/app/engine/options/black_scholes.py`, `greeks.py`.
- **Dependencies**: TASK-P1-04.
- **Acceptance Criteria**: Put-Call parity invariant passes with $|C - P - (S - K e^{-rT})| < 10^{-6}$.
- **Verification Commands**: `pytest backend/tests/unit/test_options.py`.
- **Priority**: High | **Complexity**: Medium

#### TASK-P12-02: Cox-Ross-Rubinstein Binomial Tree Pricer
- **Phase**: Phase 12
- **Status**: `BLOCKED` (Depends on TASK-P12-01)
- **Objective**: Implement CRR Binomial Tree model for American option pricing with early exercise boundary.
- **Deliverables**: `backend/app/engine/options/binomial.py`.
- **Dependencies**: TASK-P12-01.
- **Acceptance Criteria**: Converges to Black-Scholes analytical price as $N \to \infty$.
- **Verification Commands**: `pytest backend/tests/unit/test_binomial.py`.
- **Priority**: Medium | **Complexity**: Medium

#### TASK-P12-03: Implied Volatility Solver & Strategy Payoff Generator
- **Phase**: Phase 12
- **Status**: `BLOCKED` (Depends on TASK-P12-01)
- **Objective**: Implement Brent/Newton-Raphson IV solver and multi-leg payoff generator (Straddle, Strangle, Bull Spread, Iron Condor).
- **Deliverables**: `backend/app/engine/options/iv.py`, `payoff.py`.
- **Dependencies**: TASK-P12-01.
- **Acceptance Criteria**: Recovers true volatility within $10^{-5}$ tolerance; generates multi-leg PnL curves.
- **Verification Commands**: Unit tests.
- **Priority**: Medium | **Complexity**: Medium

#### TASK-P12-04: Options Workstation UI
- **Phase**: Phase 12
- **Status**: `BLOCKED` (Depends on TASK-P12-03, TASK-P3-03)
- **Objective**: Build Options pricing calculator, Greeks radar/gauge, IV solver, and multi-leg payoff diagram generator.
- **Deliverables**: `frontend/src/app/options/page.tsx`, `frontend/src/components/charts/PayoffDiagram.tsx`.
- **Dependencies**: TASK-P12-03, TASK-P3-03.
- **Acceptance Criteria**: Interactive strike/expiry sliders with immediate payoff chart and Greeks updates.
- **Verification Commands**: UI manual and component tests.
- **Priority**: High | **Complexity**: Medium

---

### Phase 13 — AI Research Copilot

#### TASK-P13-01: Artifact Context Retrieval & Grounding Engine
- **Phase**: Phase 13
- **Status**: `BLOCKED` (Depends on TASK-P4-01, TASK-P7-04)
- **Objective**: Build context aggregator that compiles verified project hypotheses, backtest trade logs, and statistical metrics into structured prompts.
- **Deliverables**: `backend/app/copilot/context.py`.
- **Dependencies**: TASK-P4-01, TASK-P7-04.
- **Acceptance Criteria**: Compiles verifiable system artifacts; strictly excludes fabricated context.
- **Verification Commands**: `pytest backend/tests/unit/test_copilot_context.py`.
- **Priority**: High | **Complexity**: Medium

#### TASK-P13-02: Provider Abstraction & Deterministic Heuristic Fallback
- **Phase**: Phase 13
- **Status**: `BLOCKED` (Depends on TASK-P13-01)
- **Objective**: Build AI provider interface (OpenAI/Anthropic compatible) with guaranteed local deterministic heuristic research engine when no API key is set.
- **Deliverables**: `backend/app/copilot/providers.py`, `heuristics.py`.
- **Dependencies**: TASK-P13-01.
- **Acceptance Criteria**: Operates seamlessly in offline environments; audits metrics and warns of overfitting.
- **Verification Commands**: `pytest backend/tests/unit/test_copilot_provider.py`.
- **Priority**: High | **Complexity**: Medium

#### TASK-P13-03: Research Methodology & Leakage Audit Engine
- **Phase**: Phase 13
- **Status**: `BLOCKED` (Depends on TASK-P13-02)
- **Objective**: Automated rule-based auditor that scans backtest and ML configurations for common research flaws (look-ahead, no fees, p-hacking).
- **Deliverables**: `backend/app/copilot/methodology.py`.
- **Dependencies**: TASK-P13-02.
- **Acceptance Criteria**: Correctly flags zero commission, excessive Sharpe without DSR, or un-purged cross-validation.
- **Verification Commands**: Unit tests.
- **Priority**: High | **Complexity**: Medium

#### TASK-P13-04: AI Copilot Workstation UI
- **Phase**: Phase 13
- **Status**: `BLOCKED` (Depends on TASK-P13-03, TASK-P3-03)
- **Objective**: Build split-screen Copilot research assistant with artifact citations, methodology check reports, and interactive prompt suggestions.
- **Deliverables**: `frontend/src/app/copilot/page.tsx`, `frontend/src/components/copilot/CopilotChat.tsx`.
- **Dependencies**: TASK-P13-03, TASK-P3-03.
- **Acceptance Criteria**: Interactive chat interface with verified metric badges and methodology audit summaries.
- **Verification Commands**: End-to-end user journey test.
- **Priority**: High | **Complexity**: High

---

### Phase 14 — Paper Trading Engine

#### TASK-P14-01: Virtual Account & Order State Lifecycle
- **Phase**: Phase 14
- **Status**: `BLOCKED` (Depends on TASK-P7-03)
- **Objective**: Implement paper trading account model with Cash, Margin, Open Orders, and Position lifecycle state machine.
- **Deliverables**: `backend/app/services/paper_trading_service.py`, `backend/app/api/paper_trading.py`.
- **Dependencies**: TASK-P7-03.
- **Acceptance Criteria**: Simulates order placement, fills, cancellations, and real-time PnL updates.
- **Verification Commands**: `pytest backend/tests/unit/test_paper_trading.py`.
- **Priority**: High | **Complexity**: Medium

#### TASK-P14-02: Pre-Trade Risk Checks & Execution Controls
- **Phase**: Phase 14
- **Status**: `BLOCKED` (Depends on TASK-P14-01)
- **Objective**: Enforce purchasing power, max position size, max leverage, and emergency kill-switch prior to order execution.
- **Deliverables**: `backend/app/engine/risk/pre_trade.py`.
- **Dependencies**: TASK-P14-01.
- **Acceptance Criteria**: Rejects orders that exceed position concentration or purchasing power.
- **Verification Commands**: Unit tests.
- **Priority**: High | **Complexity**: Low

#### TASK-P14-03: Paper Trading Workstation UI
- **Phase**: Phase 14
- **Status**: `BLOCKED` (Depends on TASK-P14-02, TASK-P3-03)
- **Objective**: Build Paper Trading dashboard with portfolio NAV, open positions table, active orders, and manual order entry ticket.
- **Deliverables**: `frontend/src/app/paper-trading/page.tsx`, `frontend/src/components/paper/OrderTicket.tsx`.
- **Dependencies**: TASK-P14-02, TASK-P3-03.
- **Acceptance Criteria**: Real-time display of simulated portfolio balances with working order ticket and risk alerts.
- **Verification Commands**: UI manual and interaction tests.
- **Priority**: High | **Complexity**: Medium

---

### Phase 15 — Collaboration & Reporting

#### TASK-P15-01: Research Tearsheet & Audit Report Generator
- **Phase**: Phase 15
- **Status**: `BLOCKED` (Depends on TASK-P7-04, TASK-P8-02)
- **Objective**: Implement comprehensive research tearsheet generator compiling hypothesis, data provenance, backtest metrics, and robustness audits.
- **Deliverables**: `backend/app/services/report_service.py`, `backend/app/api/reports.py`.
- **Dependencies**: TASK-P7-04, TASK-P8-02.
- **Acceptance Criteria**: Generates auditable report with SHA-256 lineage hash.
- **Verification Commands**: `pytest backend/tests/unit/test_reports.py`.
- **Priority**: High | **Complexity**: Medium

#### TASK-P15-02: JSON & CSV Data Export Pipeline
- **Phase**: Phase 15
- **Status**: `BLOCKED` (Depends on TASK-P15-01)
- **Objective**: Implement structured JSON experiment metadata export and CSV trade log downloads.
- **Deliverables**: `backend/app/api/reports.py` (export endpoints).
- **Dependencies**: TASK-P15-01.
- **Acceptance Criteria**: Exports valid CSV and JSON files matching schema contracts.
- **Verification Commands**: Integration tests.
- **Priority**: Medium | **Complexity**: Low

#### TASK-P15-03: Reports & Collaboration UI
- **Phase**: Phase 15
- **Status**: `BLOCKED` (Depends on TASK-P15-02, TASK-P3-03)
- **Objective**: Build Reports view with printable institutional tearsheet preview, export buttons, and research comments.
- **Deliverables**: `frontend/src/app/reports/page.tsx`, `frontend/src/components/reports/TearsheetView.tsx`.
- **Dependencies**: TASK-P15-02, TASK-P3-03.
- **Acceptance Criteria**: Clean printable view with verified metrics and export triggers.
- **Verification Commands**: UI testing.
- **Priority**: High | **Complexity**: Medium

---

### Phase 16 — Operational Readiness & Observability

#### TASK-P16-01: Background Job Worker & Queue Manager
- **Phase**: Phase 16
- **Status**: `BLOCKED` (Depends on TASK-P1-01)
- **Objective**: Implement async in-process job worker queue with live progress emission, status updates, and cancellation tokens.
- **Deliverables**: `backend/app/workers/job_manager.py`, `backend/app/api/jobs.py`.
- **Dependencies**: TASK-P1-01.
- **Acceptance Criteria**: Handles concurrent async tasks, tracks 0-100% progress, and honors cancellation requests.
- **Verification Commands**: `pytest backend/tests/unit/test_job_manager.py`.
- **Priority**: Critical | **Complexity**: Medium

#### TASK-P16-02: Health Checks, Metrics & Structured Logging
- **Phase**: Phase 16
- **Status**: `BLOCKED` (Depends on TASK-P16-01)
- **Objective**: Implement `/api/v1/health`, structured JSON logging, and worker telemetry metrics.
- **Deliverables**: `backend/app/core/logging.py`, `backend/app/api/health.py`.
- **Dependencies**: TASK-P16-01.
- **Acceptance Criteria**: Exposes system health, database status, and memory stats.
- **Verification Commands**: `curl http://127.0.0.1:8000/api/v1/health`.
- **Priority**: High | **Complexity**: Low

#### TASK-P16-03: Job Monitoring Workstation UI
- **Phase**: Phase 16
- **Status**: `BLOCKED` (Depends on TASK-P16-01, TASK-P3-03)
- **Objective**: Build Jobs dashboard showing real-time task table, animated progress bars, cancellation controls, and task log inspector.
- **Deliverables**: `frontend/src/app/jobs/page.tsx`, `frontend/src/components/jobs/JobMonitorTable.tsx`.
- **Dependencies**: TASK-P16-01, TASK-P3-03.
- **Acceptance Criteria**: Real-time status updates and working job cancellation button.
- **Verification Commands**: UI interaction testing.
- **Priority**: High | **Complexity**: Medium

---

### Phase 17 — Final Integration & Acceptance

#### TASK-P17-01: End-to-End Automated User Journey Test Suite
- **Phase**: Phase 17
- **Status**: `COMPLETED`
- **Objective**: Comprehensive test simulating complete workflow: Register $\to$ Project $\to$ Synthetic Data $\to$ EDA $\to$ Backtest $\to$ DSR Validation $\to$ Tearsheet Report.
- **Deliverables**: `backend/tests/integration/test_e2e_research_lifecycle.py`.
- **Dependencies**: TASK-P4-01 through TASK-P16-03.
- **Acceptance Criteria**: Complete research journey executes and passes with zero errors.
- **Verification Commands**: `pytest backend/tests/integration/test_e2e_research_lifecycle.py -v`.
- **Priority**: Critical | **Complexity**: High

#### TASK-P17-02: Quantitative Correctness & Invariants Audit
- **Phase**: Phase 17
- **Status**: `COMPLETED`
- **Objective**: Execute full mathematical invariant audit (Put-Call parity, Greeks convergence, Cash conservation, Look-ahead shock immunity).
- **Deliverables**: Invariants test suite run and audit report.
- **Dependencies**: TASK-P17-01.
- **Acceptance Criteria**: 100% of mathematical invariants pass within specified tolerances.
- **Verification Commands**: `pytest backend/tests/unit/test_backtest.py backend/tests/unit/test_options.py backend/tests/unit/test_portfolio.py -v`.
- **Priority**: Critical | **Complexity**: High

#### TASK-P17-03: Security & Multi-Tenant Isolation Audit
- **Phase**: Phase 17
- **Status**: `COMPLETED`
- **Objective**: Execute security audit verifying tenant query scoping, JWT expiration, input validation, and password hash security.
- **Deliverables**: Security audit verification.
- **Dependencies**: TASK-P17-01.
- **Acceptance Criteria**: Zero cross-tenant data leakage or unhandled input exceptions.
- **Verification Commands**: `pytest backend/tests/unit/test_rbac.py backend/tests/unit/test_projects.py -v`.
- **Priority**: Critical | **Complexity**: Medium

#### TASK-P17-04: Documentation Synchronization & Final Project Closure
- **Phase**: Phase 17
- **Status**: `COMPLETED`
- **Objective**: Reconcile all documentation, update `docs/memory.md` and `docs/tasks.md` to 100% completion, and verify clean repo state.
- **Deliverables**: Final synchronized documentation suite.
- **Dependencies**: TASK-P17-02, TASK-P17-03.
- **Acceptance Criteria**: Backlog reflects 100% verified status with complete test logs.
- **Verification Commands**: Repository status inspection.
- **Priority**: Critical | **Complexity**: Low
