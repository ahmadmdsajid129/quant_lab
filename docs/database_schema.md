# QuantLab Relational Database Schema Specification

**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Database Engines:** SQLite (Local Dev / Offline Tests), PostgreSQL (Production Multi-tenant)  
**ORM:** SQLAlchemy 2.0 with Alembic Migrations  

---

## 1. Relational Entities Specification

### 1.1 `users`
Stores user authentication and identity credentials.
- `id` (VARCHAR(36), PK): UUID v4.
- `email` (VARCHAR(255), UNIQUE, NOT NULL): Indexed user email.
- `hashed_password` (VARCHAR(255), NOT NULL): bcrypt hashed password.
- `full_name` (VARCHAR(255), NOT NULL): Display name.
- `is_active` (BOOLEAN, DEFAULT TRUE): Account status.
- `created_at` (TIMESTAMP UTC, NOT NULL).
- `updated_at` (TIMESTAMP UTC, NOT NULL).

### 1.2 `workspaces`
Tenancy boundary for projects, datasets, and experiments.
- `id` (VARCHAR(36), PK): UUID v4.
- `name` (VARCHAR(255), NOT NULL): Workspace name.
- `slug` (VARCHAR(255), UNIQUE, NOT NULL): URL-friendly slug.
- `owner_id` (VARCHAR(36), FK -> `users.id`, NOT NULL).
- `created_at` (TIMESTAMP UTC, NOT NULL).

### 1.3 `workspace_members`
Role-Based Access Control mapping users to workspaces.
- `id` (VARCHAR(36), PK): UUID v4.
- `workspace_id` (VARCHAR(36), FK -> `workspaces.id`, NOT NULL).
- `user_id` (VARCHAR(36), FK -> `users.id`, NOT NULL).
- `role` (VARCHAR(50), NOT NULL): `'ADMIN' | 'RESEARCHER' | 'VIEWER'`.
- Unique constraint: `(workspace_id, user_id)`.

### 1.4 `projects`
Quantitative research projects grouping hypotheses and experiments.
- `id` (VARCHAR(36), PK): UUID v4.
- `workspace_id` (VARCHAR(36), FK -> `workspaces.id`, NOT NULL, INDEXED).
- `title` (VARCHAR(255), NOT NULL).
- `description` (TEXT).
- `asset_class` (VARCHAR(100), NOT NULL): `'EQUITIES' | 'CRYPTO' | 'FX' | 'DERIVATIVES' | 'MULTI_ASSET'`.
- `status` (VARCHAR(50), NOT NULL): `'DRAFT' | 'IN_PROGRESS' | 'VALIDATED' | 'REJECTED' | 'ARCHIVED'`.
- `created_at` (TIMESTAMP UTC, NOT NULL).
- `updated_at` (TIMESTAMP UTC, NOT NULL).

### 1.5 `hypotheses`
Formal mathematical and market hypothesis tracking.
- `id` (VARCHAR(36), PK): UUID v4.
- `project_id` (VARCHAR(36), FK -> `projects.id`, NOT NULL, INDEXED).
- `statement` (TEXT, NOT NULL): Formal research hypothesis.
- `mechanism` (TEXT, NOT NULL): Proposed underlying financial/economic mechanism.
- `predicted_outcome` (TEXT, NOT NULL): Quantitative expectation.
- `falsification_criteria` (TEXT, NOT NULL): Criteria under which the hypothesis is rejected.
- `status` (VARCHAR(50), NOT NULL): `'UNTESTED' | 'SUPPORTED' | 'FALSIFIED'`.
- `created_at` (TIMESTAMP UTC, NOT NULL).

### 1.6 `datasets`
Catalog of historical and synthetic market data.
- `id` (VARCHAR(36), PK): UUID v4.
- `workspace_id` (VARCHAR(36), FK -> `workspaces.id`, NOT NULL, INDEXED).
- `symbol` (VARCHAR(50), NOT NULL, INDEXED).
- `name` (VARCHAR(255), NOT NULL).
- `source` (VARCHAR(50), NOT NULL): `'STOOQ' | 'SYNTHETIC' | 'YAHOO' | 'CSV'`.
- `timeframe` (VARCHAR(20), NOT NULL): `'1m' | '5m' | '1h' | '1d'`.
- `start_date` (TIMESTAMP UTC, NOT NULL).
- `end_date` (TIMESTAMP UTC, NOT NULL).
- `total_bars` (INTEGER, NOT NULL).
- `parquet_path` (VARCHAR(512), NOT NULL): Relative path to columnar Parquet file.
- `quality_score` (FLOAT, NOT NULL): 0.0 - 100.0%.
- `quality_audit` (JSON, NOT NULL): Detailed JSON record of anomalies and checks.
- `created_at` (TIMESTAMP UTC, NOT NULL).

### 1.7 `strategies`
Configured strategy templates and parameter sets.
- `id` (VARCHAR(36), PK): UUID v4.
- `project_id` (VARCHAR(36), FK -> `projects.id`, NOT NULL, INDEXED).
- `name` (VARCHAR(255), NOT NULL).
- `strategy_type` (VARCHAR(100), NOT NULL): `'BUY_AND_HOLD' | 'MA_CROSSOVER' | 'MOMENTUM' | 'MEAN_REVERSION' | 'CUSTOM'`.
- `parameters` (JSON, NOT NULL): Strategy hyperparameter dictionary.
- `version` (INTEGER, NOT NULL, DEFAULT 1).
- `created_at` (TIMESTAMP UTC, NOT NULL).

### 1.8 `experiments`
Execution records of backtests, ML model runs, and optimizations.
- `id` (VARCHAR(36), PK): UUID v4.
- `project_id` (VARCHAR(36), FK -> `projects.id`, NOT NULL, INDEXED).
- `strategy_id` (VARCHAR(36), FK -> `strategies.id`, NULLABLE).
- `dataset_id` (VARCHAR(36), FK -> `datasets.id`, NOT NULL).
- `experiment_type` (VARCHAR(50), NOT NULL): `'BACKTEST' | 'WALK_FORWARD' | 'ML_TRAIN' | 'PORTFOLIO_OPT'`.
- `config` (JSON, NOT NULL): Execution configuration (capital, fees, slippage, seeds).
- `metrics` (JSON, NOT NULL): Quantitative output metrics (Sharpe, MaxDD, CAGR, WinRate, DSR).
- `status` (VARCHAR(50), NOT NULL): `'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED'`.
- `start_time` (TIMESTAMP UTC, NOT NULL).
- `end_time` (TIMESTAMP UTC, NULLABLE).
- `lineage_hash` (VARCHAR(64), NOT NULL): SHA-256 hash of (dataset_hash + config + code_version).

### 1.9 `trade_logs`
Chronological record of simulated trades generated during backtests.
- `id` (VARCHAR(36), PK): UUID v4.
- `experiment_id` (VARCHAR(36), FK -> `experiments.id`, NOT NULL, INDEXED).
- `symbol` (VARCHAR(50), NOT NULL).
- `entry_time` (TIMESTAMP UTC, NOT NULL).
- `exit_time` (TIMESTAMP UTC, NOT NULL).
- `side` (VARCHAR(10), NOT NULL): `'LONG' | 'SHORT'`.
- `quantity` (FLOAT, NOT NULL).
- `entry_price` (FLOAT, NOT NULL).
- `exit_price` (FLOAT, NOT NULL).
- `gross_pnl` (FLOAT, NOT NULL).
- `fees` (FLOAT, NOT NULL).
- `net_pnl` (FLOAT, NOT NULL).
- `return_pct` (FLOAT, NOT NULL).

### 1.10 `jobs`
Background worker task tracker.
- `id` (VARCHAR(36), PK): UUID v4.
- `job_type` (VARCHAR(50), NOT NULL): `'BACKTEST' | 'DATA_INGEST' | 'ML_TRAIN' | 'VALIDATION'`.
- `status` (VARCHAR(50), NOT NULL): `'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED'`.
- `progress` (FLOAT, DEFAULT 0.0): 0.0 to 100.0%.
- `error_message` (TEXT, NULLABLE).
- `created_at` (TIMESTAMP UTC, NOT NULL).
- `completed_at` (TIMESTAMP UTC, NULLABLE).

---

## 2. Indexes & Performance Optimization
- `idx_projects_workspace_id`: Foreign key lookup optimization.
- `idx_datasets_workspace_symbol`: Fast symbol resolution within tenant.
- `idx_experiments_project_status`: Efficient experiment listing and filtering.
- `idx_trade_logs_experiment_id`: Rapid pagination and chart retrieval for backtest trades.
