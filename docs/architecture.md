# QuantLab System Architecture Specification

**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Classification:** Core System Architecture  

---

## 1. System Overview & Technology Stack

QuantLab adopts a clean, decoupled architecture:
- **Frontend Layer**: Next.js 14+ (App Router), React, TypeScript, Tailwind CSS, Lucide icons, Financial Charting components. Designed as a high-density, institutional-grade quantitative workstation.
- **API & Application Layer**: FastAPI (Python 3.13), Pydantic v2 schemas, Dependency Injection, Starlette middleware, JWT authentication.
- **Domain & Quantitative Engine Layer**: Pure Python, NumPy, pandas, SciPy, statsmodels, scikit-learn. Vectorized matrix operations for fast screening; event-driven state-machine for realistic microstructure and execution simulation.
- **Persistence & Storage Layer**:
  - Relational Metadata: PostgreSQL in production; SQLite for zero-config local development and testing, unified via SQLAlchemy 2.0 ORM and Alembic migrations.
  - Time-Series Storage: High-performance columnar Apache Parquet files organized by dataset ID, instrument, and resolution.
- **Execution & Background Worker Layer**: Async worker queue with job lifecycle management, live progress reporting, cancellation, and execution isolation.

---

## 2. Mermaid Diagrams Suite

### 2.1 Diagram 1: Overall System Architecture

```mermaid
flowchart TB
    subgraph Client["Frontend Workstation (Next.js / TypeScript / React)"]
        UI_Shell[Institutional Shell & Workspace Selector]
        Views[Research, Data, Backtest, ML, LOB, Options, Copilot Views]
        State[Zustand Store / TanStack Query Client]
        UI_Shell --> Views --> State
    end

    subgraph Gateway["API Gateway & Web Server (FastAPI)"]
        AuthMid[Auth & RBAC Middleware]
        RateLim[Rate Limiter]
        Router[REST & WebSocket Router]
        AuthMid --> RateLim --> Router
    end

    subgraph AppService["Application Services Layer"]
        ProjectSvc[Project & Hypothesis Service]
        DataSvc[Data Ingestion & Quality Service]
        BacktestSvc[Backtest & Experiment Service]
        MLSvc[ML & Feature Pipeline Service]
        PortSvc[Portfolio & Risk Service]
        LOBSvc[Microstructure & LOB Service]
        OptSvc[Options Pricing Service]
        CopilotSvc[AI Copilot Context Service]
    end

    subgraph QuantEngine["Quantitative Engine (NumPy / SciPy / Sklearn)"]
        VectorEngine[Vectorized Analysis Engine]
        EventEngine[Event-Driven Simulation Engine]
        StatsEngine[Statistical Validation & DSR]
        LOBEngine[Order Book Matching Engine]
        OptEngine[Black-Scholes & Greeks Engine]
    end

    subgraph Workers["Async Worker Subsystem"]
        JobQueue[Async Job Queue & Worker Pool]
        JobTracker[Progress & Cancellation Tracker]
    end

    subgraph Storage["Persistence & Artifact Storage"]
        SQL[(Relational DB: SQLite / PostgreSQL)]
        Parquet[(Columnar Time-Series Parquet Store)]
        Artifacts[(Artifact & Report Store)]
    end

    State <==>|HTTP / WebSocket| Gateway
    Router --> AppService
    AppService --> QuantEngine
    AppService --> Workers
    Workers --> QuantEngine
    AppService --> Storage
    QuantEngine --> Parquet
```

---

### 2.2 Diagram 2: Research Execution Flow

```mermaid
flowchart LR
    H[1. Formulate Hypothesis] --> D[2. Select / Ingest Dataset]
    D --> S[3. Configure Strategy & Costs]
    S --> B[4. Run Backtest Event Engine]
    B --> V[5. Statistical Validation & DSR]
    V --> P[6. Portfolio Allocation / ML]
    P --> R[7. Generate Verifiable Report]
    R --> C[8. AI Copilot Review & Audit]
```

---

### 2.3 Diagram 3: Market Data Ingestion & Normalization

```mermaid
flowchart TD
    Raw[External Feed / CSV / Synthetic] --> IngestAdapter[Provider Adapter Interface]
    IngestAdapter --> Normalize[Timestamp UTC & Schema Normalizer]
    Normalize --> QA[Data Quality & Anomaly Audit]
    QA -->|Passed| WriteParquet[Write Columnar Parquet Store]
    QA -->|Passed| IndexSQL[Register Dataset in SQL Catalog]
    QA -->|Failed| Alert[Log Quality Violations & Reject]
```

---

### 2.4 Diagram 4: Backtesting Engine Architecture

```mermaid
flowchart TD
    subgraph TimeLoop["Bar-by-Bar Progression (t = 0 to T)"]
        Bar_t[Receive Bar t Data]
        State_t[Update Portfolio Valuation at t]
        Sig_t[Strategy evaluates signals using ONLY data <= t]
        Order_t[Generate Orders for execution at t+1 Open]
    end

    subgraph FillExecution["Execution Modeling (t + 1)"]
        Bar_next[Receive Bar t+1 Open Price]
        CostModel[Apply Spread, Slippage & Commission]
        Fill[Execute Fill & Update Cash / Position]
        AuditLog[Record Chronological Trade Log Entry]
    end

    Sig_t --> Order_t
    Order_t --> Bar_next
    Bar_next --> CostModel --> Fill --> AuditLog
    Fill --> State_t
```

---

### 2.5 Diagram 5: Machine Learning Experimentation Pipeline

```mermaid
flowchart TD
    RawData[Normalized Time Series] --> FeatEng[Feature Construction: Lagged, Vol, Mom]
    FeatEng --> ChronoSplit[Strict Chronological Split: Train / Val / Test]
    ChronoSplit --> ScaleTrain[Fit Preprocessors ONLY on Train]
    ScaleTrain --> TransformAll[Transform Train, Val, Test]
    TransformAll --> TrainModel[Train Supervised Model: RF / GBDT]
    TrainModel --> ValEval[Evaluate Out-of-Sample Performance]
    ValEval --> SHAP[Compute SHAP & Feature Importance]
    ValEval --> EconomicEval[Simulate Trading Returns & Turnover]
    EconomicEval --> DriftCheck[Kolmogorov-Smirnov Drift Test]
```

---

### 2.6 Diagram 6: Background Job Lifecycle

```mermaid
stateDiagram-v2
    [*] --> QUEUED: Job Submitted
    QUEUED --> RUNNING: Worker Picks Up
    RUNNING --> PROGRESS_UPDATE: Periodic Progress Emission (0-100%)
    PROGRESS_UPDATE --> RUNNING
    RUNNING --> COMPLETED: Execution Succeeded
    RUNNING --> FAILED: Exception Caught & Logged
    RUNNING --> CANCELLED: Cancellation Requested by User
    COMPLETED --> [*]
    FAILED --> [*]
    CANCELLED --> [*]
```

---

### 2.7 Diagram 7: Authentication & Access Control

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend
    participant AuthAPI as /api/v1/auth
    participant DBOps as Database
    participant ProtectedAPI as /api/v1/projects

    User->>Frontend: Enter credentials (email, password)
    Frontend->>AuthAPI: POST /login {email, password}
    AuthAPI->>DBOps: Verify password hash (bcrypt)
    DBOps-->>AuthAPI: User record & Workspace memberships
    AuthAPI-->>Frontend: Return JWT token & User info
    Frontend->>ProtectedAPI: GET /projects (Bearer token in Header)
    ProtectedAPI->>ProtectedAPI: Validate JWT signature & extract user_id
    ProtectedAPI->>DBOps: Query projects WHERE workspace_id IN user_workspaces
    DBOps-->>ProtectedAPI: Authorized projects only
    ProtectedAPI-->>Frontend: 200 OK (Scoped project list)
```

---

### 2.8 Diagram 8: Core Relational Database Entities

```mermaid
erDiagram
    USERS ||--o{ WORKSPACE_MEMBERS : has
    WORKSPACES ||--o{ WORKSPACE_MEMBERS : contains
    WORKSPACES ||--o{ PROJECTS : owns
    PROJECTS ||--o{ HYPOTHESES : defines
    PROJECTS ||--o{ EXPERIMENTS : executes
    PROJECTS ||--o{ STRATEGIES : includes
    WORKSPACES ||--o{ DATASETS : stores
    EXPERIMENTS ||--o{ TRADE_LOGS : records
    EXPERIMENTS ||--o{ REPORTS : generates
    USERS ||--o{ AUDIT_LOGS : performs

    USERS {
        uuid id PK
        string email
        string hashed_password
        string full_name
        datetime created_at
    }
    WORKSPACES {
        uuid id PK
        string name
        string slug
    }
    PROJECTS {
        uuid id PK
        uuid workspace_id FK
        string title
        string status
    }
    EXPERIMENTS {
        uuid id PK
        uuid project_id FK
        string experiment_type
        jsonb metrics
        jsonb config
        string status
    }
```

---

### 2.9 Diagram 9: AI Copilot Grounded Context Flow

```mermaid
flowchart TD
    UserQuery[User Prompt: e.g. Why did Strategy B fail in 2022?] --> CopilotRouter[Copilot Context Assembler]
    CopilotRouter --> FetchExp[Retrieve Experiment & Trade Logs from SQL]
    CopilotRouter --> FetchMetrics[Retrieve Sharpe, Drawdown, VaR, DSR]
    CopilotRouter --> FetchMarket[Retrieve 2022 Volatility & Regime Data]
    FetchExp & FetchMetrics & FetchMarket --> GroundedPrompt[Assemble Grounded System Prompt with Verified Facts]
    GroundedPrompt --> AIModel[AI Provider / Local Heuristic Engine]
    AIModel --> VerifiedResponse[Output Explanation with Artifact Citations & Limitations]
```

---

### 2.10 Diagram 10: Deployment Architecture

```mermaid
flowchart TB
    subgraph Host["Host Environment (Native or Containerized)"]
        subgraph WebTier["Frontend Tier (Port 3000)"]
            NextServer[Next.js App Server (Node.js 26)]
        end
        subgraph APITier["Backend Tier (Port 8000)"]
            FastAPIServer[Uvicorn / FastAPI API (Python 3.13)]
            AsyncWorkerPool[Background Job Worker Pool]
        end
        subgraph DataTier["Storage Tier"]
            SQLiteDB[(SQLite / PostgreSQL Database)]
            ParquetVolume[(Local Parquet Filesystem: ./data/parquet)]
        end
    end
    ClientBrowser[User Web Browser] <==> NextServer
    NextServer <==>|Reverse Proxy / Internal HTTP| FastAPIServer
    FastAPIServer --> AsyncWorkerPool
    FastAPIServer --> SQLiteDB
    FastAPIServer --> ParquetVolume
    AsyncWorkerPool --> ParquetVolume
```

---

## 3. Subsystem Breakdown & Architectural Decisions

### 3.1 Quantitative Engine Design
The quantitative engine is strictly decoupled from web protocols. All math algorithms accept standard NumPy arrays, pandas DataFrames, or pure Python primitives and return structured dictionary/Pydantic models.
- **Vectorized Module (`engine/backtest/vectorized.py`)**: Uses matrix operations for ultra-fast signal evaluation, indicator calculation (RSI, SMA, EMA, MACD, Bollinger), and rapid preliminary performance ranking.
- **Event-Driven Module (`engine/backtest/event.py`)**: Models discrete time transitions. Manages Portfolio, Position, and Order state machines. Computes cash flows, commissions, slippage, and borrow financing bar-by-bar.
- **Microstructure Module (`engine/microstructure/lob.py`)**: In-memory double auction order book. Maintains Bid and Ask heaps/price levels with queue FIFO tracking.
- **Options Pricing Module (`engine/options/pricer.py`)**: Exact Black-Scholes analytical formulas, Greeks derivation, CRR binomial tree for American options, and numerical implied volatility solvers.

### 3.2 Persistent Data Management
1. **Application State**: Handled via SQLAlchemy 2.0 with asynchronous and synchronous sessions. Migrations handled by Alembic.
2. **Financial Time-Series**: Stored in columnar Apache Parquet. Parquet provides 10x-50x compression, zero-copy reads via pyarrow, and eliminates database bloat from storing millions of tick/bar records in relational rows.
