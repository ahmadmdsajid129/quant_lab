# QuantLab Engineering & Coding-Agent Rules

**Document Version:** 1.0.0  
**Status:** Enforceable Mandate  
**Classification:** Engineering Standards & Constraints  

---

## 1. Absolute Prohibitions (Zero Tolerance)

The following practices are strictly prohibited in the QuantLab codebase. Any pull request, automated agent contribution, or code commit containing any of these violations will be rejected immediately:

1. **No Look-Ahead Bias**:
   - In any backtest or simulation, signal generation at bar $t$ using close price $C_t$ must never be assumed to execute at $C_t$ unless an explicit bar-close execution latency and slippage model is declared and tested.
   - Standard execution default: Signal at bar $t$ executes at bar $t+1$ Open.
2. **No Data Leakage in Machine Learning**:
   - Feature normalizers, imputers, scalers, and target encoders must be fitted **exclusively** on training partitions ($D_{\text{train}}$) and only applied (never re-fitted) to validation and test partitions ($D_{\text{val}}, D_{\text{test}}$).
   - Time-series cross-validation must strictly respect chronological ordering. K-fold with random shuffling on time-series data is an automatic rejection.
3. **No Fabricated or Hardcoded Financial Metrics**:
   - All Sharpe ratios, drawdowns, annual returns, VaR, and p-values returned by the system must be computed by actual mathematical routines from real trade logs or price arrays.
   - Never stub a backend endpoint with static numbers such as `sharpe_ratio: 2.14` or `max_drawdown: 0.08` to make a UI look complete.
4. **No Arbitrary Code Execution in API Process**:
   - User-supplied strategy logic or formulas must never be evaluated via `eval()`, `exec()`, or unconstrained shell calls in the web request thread.
   - Strategy definitions must use declarative parameters or validated domain DSLs / isolated execution workers.
5. **No Hardcoded Secrets or Credentials**:
   - No API keys, JWT secrets, passwords, or tokens in source code. All configuration must be loaded via environment variables using Pydantic `BaseSettings`.
6. **No Fake Completed Features**:
   - Do not create buttons, dropdowns, forms, or tabs that do nothing or log "TODO" to the console without backend connection.
   - Do not claim a task is completed in `docs/tasks.md` unless its acceptance criteria have passed automated testing.
7. **No Untested Destructive Database Operations**:
   - No `DROP TABLE` or destructive data loss migrations in production paths. All schema evolutions must be tracked in reversible Alembic migrations.

---

## 2. Quantitative Correctness Rules

### 2.1 Time Semantics & Information Availability
- Timestamping must be unified to UTC.
- Each bar $(t)$ contains: `timestamp`, `open`, `high`, `low`, `close`, `volume`.
- A signal calculated after the close of bar $t$ has timestamp $t$. It is made available to the portfolio allocator at $t$.
- Orders submitted based on signal $t$ can only be filled at or after $t + \Delta t$, where $\Delta t \ge 1 \text{ tick}$ (typically bar $t+1$ Open).

### 2.2 Cash & Position Accounting Invariants
- Cash balance must be updated after every transaction:
  $$\text{Cash}_{t+1} = \text{Cash}_t - \text{Filled Shares} \times \text{Execution Price} - \text{Commissions} - \text{Borrow Fees}$$
- Portfolio Value:
  $$\text{NAV}_t = \text{Cash}_t + \sum_{i} \text{Shares}_{i,t} \times \text{Price}_{i,t}$$
- Short positions require borrow fee accrual:
  $$\text{Borrow Fee} = |\text{Short Market Value}| \times \frac{\text{Borrow Rate}}{360 \text{ or } 252} \times \Delta t$$
- Transaction costs (spread + slippage + commission) must be explicitly deducted.

### 2.3 Mathematical Robustness
- **Division by Zero Protection**: All Sharpe ratio calculations must handle $\sigma = 0$:
  $$\text{Sharpe} = \begin{cases} \frac{\mu - r_f}{\sigma} & \text{if } \sigma > 10^{-8} \\ 0.0 & \text{otherwise} \end{cases}$$
- **Drawdown Invariant**: Maximum drawdown must always be $\le 0.0$ (or non-negative by convention, but never negative loss). Peak must be running cumulative maximum of equity curve.

---

## 3. Backend Engineering & Python Standards

1. **Python Version**: Python 3.11+ (targeting 3.13 compatibility).
2. **Type Hints**: 100% type hint coverage on all public functions, classes, and API endpoints using `typing` and Pydantic v2.
3. **API Contracts**: All request bodies and responses must inherit from Pydantic `BaseModel` with explicit descriptions, field constraints, and JSON examples.
4. **Error Handling**: Use custom HTTPException handlers returning consistent JSON schema:
   ```json
   {
     "error": {
       "code": "RESOURCE_NOT_FOUND",
       "message": "Project with id 123 does not exist",
       "details": {}
     }
   }
   ```
5. **Database Queries**:
   - Always query with tenant/workspace scoping (`filter(Project.workspace_id == current_workspace.id)`).
   - Use async sessions where high concurrency is required.
   - Use indexed columns for filtering and joins.

---

## 4. Frontend Engineering & Next.js Standards

1. **TypeScript Strict Mode**: No `any` types permitted. Define explicit interfaces in `src/types/`.
2. **Component Architecture**:
   - Decouple presentational components (`components/ui/`) from data-fetching containers (`components/features/`).
   - Use Server Components where appropriate, and `'use client'` only when interactive state, charts, or browser APIs are required.
3. **Data Fetching & State**:
   - Use TanStack Query (React Query) or SWR for client-side API caching and invalidation.
   - Store global workspace and user context in lightweight Zustand stores.
4. **Visual Design & Typography**:
   - Adhere strictly to the design tokens defined in `docs/design.md`.
   - Never use arbitrary inline CSS color values like `style={{ color: '#123456' }}`; use Tailwind classes mapped to theme tokens.
   - Financial numbers must use monospace tabular figures (`font-mono tabular-nums`).

---

## 5. Testing & Verification Rules

1. **Every Feature Requires Tests**:
   - New mathematical formula $\rightarrow$ Unit test verifying against analytical solution or textbook case.
   - New API route $\rightarrow$ Integration test verifying status codes (200, 400, 401, 403, 404).
   - New backtest engine component $\rightarrow$ Test verifying no look-ahead leakage and exact cash conservation.
2. **Test Command Execution**:
   - Automated agents must run `pytest` or `npm test` directly in the shell and report actual test outcomes before marking tasks complete.
