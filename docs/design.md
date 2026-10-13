# QuantLab Design System & UI Specification

**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Classification:** Visual Design & UI Architecture  

---

## 1. Brand Identity & Design Principles

QuantLab's visual interface is engineered as an **institutional quantitative research workstation**. It balances high information density, mathematical rigor, clean typographic hierarchy, and visual elegance.

### Core Principles
1. **Information Density without Clutter**: High data density with micro-spacing ($4\text{px}$ grid), tabular numerals, and compact data tables.
2. **Financial Semantic Precision**: Green/Red are strictly reserved for positive return / long position / profit and negative return / short position / loss. Cyan/Electric Blue is reserved for primary actions and active selections.
3. **Institutional Dark-First Theme**: Deep dark slate background (`#090d16`) with high-contrast neutral borders (`#1e293b`) that reduce eye strain during intensive multi-hour research sessions. A clean institutional light mode is also supported.
4. **Interactive Responsiveness**: Immediate feedback on all interactive elements: hover states, micro-transitions ($150\text{ms}$ ease), and keyboard accessibility.

---

## 2. Color Palette & Tokens (HEX Specifications)

### 2.1 Dark Mode (Primary Institutional Theme)
| Token Name | HEX Code | Purpose / Application |
| :--- | :--- | :--- |
| `--bg-base` | `#090d16` | Main application background |
| `--bg-surface` | `#0f172a` | Cards, panels, sidebars, workstation canvases |
| `--bg-surface-elevated`| `#1e293b` | Dropdowns, dialogs, popovers, table headers |
| `--border-subtle` | `#1e293b` | Default divider and container borders |
| `--border-strong` | `#334155` | Focused inputs, active borders, card outlines |
| `--text-primary` | `#f8fafc` | Headings, primary metrics, high-emphasis text |
| `--text-secondary` | `#94a3b8` | Subtitles, table headers, descriptions |
| `--text-muted` | `#64748b` | Timestamps, disabled states, helper notes |
| `--accent-primary` | `#0ea5e9` | Electric Sky / Cyan: Primary actions, active tabs |
| `--accent-primary-hover`| `#38bdf8` | Hover state for primary actions |
| `--profit-green` | `#10b981` | Positive returns, long positions, gains, success |
| `--loss-red` | `#ef4444` | Negative returns, short positions, drawdowns, errors |
| `--warning-amber` | `#f59e0b` | Warnings, potential bias alerts, high risk |
| `--info-indigo` | `#6366f1` | Neutral indicators, ML feature markers, tags |

### 2.2 Light Mode (Clean Academic Theme)
| Token Name | HEX Code | Purpose / Application |
| :--- | :--- | :--- |
| `--bg-base` | `#f8fafc` | Main application background |
| `--bg-surface` | `#ffffff` | Cards, panels, sidebars |
| `--bg-surface-elevated`| `#f1f5f9` | Dropdowns, table headers |
| `--border-subtle` | `#e2e8f0` | Dividers and borders |
| `--border-strong` | `#cbd5e1` | Input outlines, active borders |
| `--text-primary` | `#0f172a` | Primary text |
| `--text-secondary` | `#475569` | Secondary labels |
| `--text-muted` | `#94a3b8` | Hints and timestamps |
| `--accent-primary` | `#0284c7` | Primary buttons and selection states |
| `--profit-green` | `#059669` | Positive financial values |
| `--loss-red` | `#dc2626` | Negative financial values |

---

## 3. Typography & Spacing Scale

### 3.1 Font Families
- **Primary Interface**: `Inter`, `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **Monospace / Numerical Data**: `JetBrains Mono`, `ui-monospace, "Cascadia Code", "Courier New", monospace`
  - All numerical values, trade prices, dates, Sharpe ratios, and matrix cells must utilize `font-mono tabular-nums`.

### 3.2 Type Scale
- `text-xs`: $11\text{px}$ / $16\text{px}$ line-height (Badges, timestamps, table cells)
- `text-sm`: $13\text{px}$ / $18\text{px}$ line-height (Default UI body, form inputs, secondary labels)
- `text-base`: $14\text{px}$ / $20\text{px}$ line-height (Emphasized text, card titles)
- `text-lg`: $16\text{px}$ / $24\text{px}$ line-height (Section headers, subheadings)
- `text-xl`: $18\text{px}$ / $26\text{px}$ line-height (Workstation titles)
- `text-2xl`: $22\text{px}$ / $30\text{px}$ line-height (Hero metric callouts)

### 3.3 Spacing & Layout Scale (4px Base Grid)
- `space-1`: $4\text{px}$
- `space-2`: $8\text{px}$
- `space-3`: $12\text{px}$
- `space-4`: $16\text{px}$
- `space-6`: $24\text{px}$
- `space-8`: $32\text{px}$

---

## 4. Component Inventory & Patterns

### 4.1 Buttons
- **Primary**: Solid Cyan background (`#0ea5e9`), dark navy text (`#090d16`), font-weight 600, hover brightness transition.
- **Secondary**: Slate elevated surface (`#1e293b`), primary text (`#f8fafc`), subtle border (`#334155`).
- **Destructive**: Subdued Red (`#ef4444` text and border, dark red background with 10% opacity).
- **Ghost / Icon**: Transparent background, text muted (`#94a3b8`), hover surface elevation.

### 4.2 Financial Data Tables
- Sticky header with sort indicators (asc/desc arrows).
- Alternating subtle row backgrounds (`hover:bg-slate-800/40`).
- Strict right-alignment for numerical data (`text-right font-mono tabular-nums`).
- Integrated pagination and client/server search filtering.

### 4.3 Chart Styling & Micro-Visualizations
- Dark canvas background (`#090d16` or transparent over `#0f172a`).
- Gridlines in subtle slate (`#1e293b` with 0.5px dashed stroke).
- Colors:
  - Cumulative Strategy Return: Cyan (`#0ea5e9`)
  - Benchmark (e.g. S&P 500 / SPY): Neutral Slate (`#64748b`)
  - Underwater / Drawdown Area: Semi-transparent Loss Red (`#ef4444` at 20% opacity)
  - Volume Bars: Neutral Slate (`#334155`)

---

## 5. Page-by-Page Layout Specifications

### 5.1 Main Application Shell (`/`)
- **Left Navigation Rail (Sidebar)**: Compact ($240\text{px}$ width), collapsible to $64\text{px}$. Includes Workspace selector, categorized nav links with icons, status badge, and user profile avatar.
- **Top Command Bar**: Breadcrumb path, Global Quick Search (`Cmd+K`), Background Job Monitor Indicator (spinning pulse when active), Notification Tray, Environment Mode Badge (`Local / Cloud`).
- **Main Canvas**: Fluid responsive layout with `$16\text{px}$` padding, full-screen workstation expansion toggle.

### 5.2 Research Projects (`/projects`)
- Project cards grid and table view toggle.
- Metrics per card: Active Hypotheses, Latest Backtest Sharpe, Total Runs, Falsification Status.
- Quick action: "New Hypothesis & Project" modal.

### 5.3 Data Browser & Ingestion (`/data`)
- Top: Ingestion wizard (Stooq, Yahoo Finance, Synthetic Market Data Generator, CSV file upload).
- Left: Dataset catalog list with status indicators (Active, Ingesting, Stale).
- Right: Interactive OHLCV candlestick chart, summary statistics table, and automated Data Quality Audit score.

### 5.4 Strategy Editor & Library (`/strategies`)
- Strategy template selector (Buy & Hold, MA Crossover, Momentum, Mean Reversion).
- Parameter configuration form with real-time JSON validation.
- Signal definition panel and benchmark selector.

### 5.5 Backtest Configuration & Results (`/backtests`)
- Two-panel layout:
  - Left ($320\text{px}$): Backtest run parameters (Dates, Capital, Commission bps, Slippage %, Execution Semantics).
  - Right: Results dashboard:
    - Top: Key metrics cards (Sharpe, CAGR, Max Drawdown, Win Rate, Profit Factor, Turnover).
    - Middle: Interactive Equity Curve vs. Benchmark & Drawdown Chart.
    - Bottom: Tabbed pane (Trade Log, Order Log, Monthly Returns Heatmap, Cost Attribution).

### 5.6 Statistical Validation Lab (`/validation`)
- Walk-forward rolling performance chart.
- Deflated Sharpe Ratio calculation widget (shows number of trials tested vs required hurdle).
- Purged K-Fold stability score.
- Parameter sensitivity heatmap (e.g. Lookback window vs Volatility threshold).

### 5.7 Machine Learning Lab (`/ml`)
- Feature selection matrix (Lagged returns, Volatility, Momentum indicators).
- Chronological split preview (Train / Validation / Test partitions).
- Model training config (Ridge, Random Forest, HistGradientBoosting).
- Model evaluation panel: Out-of-sample ROC-AUC/MSE, SHAP feature importance plot, and Drift test results.

### 5.8 Portfolio Optimization & Risk (`/portfolio`)
- Multi-asset weight allocation selector (Equal Weight, Inverse Vol, Max Sharpe, Min Volatility).
- Covariance shrinkage selector (Ledoit-Wolf, Sample).
- Risk breakdown: Marginal Risk Contribution bar chart, historical VaR/CVaR gauge, stress scenario simulator.

### 5.9 Market Microstructure & LOB Simulator (`/microstructure`)
- Real-time Visual Limit Order Book ladder:
  - Bids in Green, Asks in Red, with cumulative depth volume bars.
- Live order event feed (Insert, Modify, Cancel, Fill).
- Microstructure stats: Spread in ticks, Midprice, Microprice, Order Flow Imbalance.
- Interactive controls: Submit simulated Limit/Market order, toggle Hawkes/Poisson event flow.

### 5.10 Options & Derivatives Lab (`/options`)
- Option contract spec: Underlying price $S$, Strike $K$, Expiry $T$, Volatility $\sigma$, Rate $r$.
- Analytical output: Call/Put Price, Delta, Gamma, Theta, Vega, Rho.
- Binomial tree visualization and Multi-leg payoff diagram generator (Straddle, Bull Spread, Iron Condor).

### 5.11 AI Research Copilot (`/copilot`)
- Split-screen research workspace:
  - Left: Active project artifacts (Hypothesis, Backtest results, Data stats).
  - Right: Chat interface with grounded prompt citations, failure diagnosis suggestions, and report drafting tools.

### 5.12 Operational Job Monitoring (`/jobs`)
- Real-time job queue table with Job ID, Task Type, Status (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`), Elapsed Time, Progress Bar, and Cancel Button.
- Detailed task log viewer modal.
