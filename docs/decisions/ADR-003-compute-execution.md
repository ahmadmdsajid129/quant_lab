# ADR-003: Compute & Background Execution Model

**Status:** Accepted  
**Date:** 2026-10-13  
**Deciders:** Principal Architect, Systems Engineer  

---

## Context
Quantitative workflows involve heavy asynchronous computations: historical backtests, parameter grid sweeps, walk-forward validation runs, ML model training, and Monte Carlo simulations. Executing these directly in HTTP request handlers would block the event loop, cause HTTP timeouts, and degrade UI responsiveness.

## Decision
We implement an asynchronous background worker subsystem within the backend architecture:
1. **Job Queue & Lifecycle**: Each heavy task receives a unique Job UUID with status tracking (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`).
2. **Worker Pool**: Async workers process tasks from an in-memory priority queue (with Redis/Celery adapter interface for distributed scaling).
3. **Progress Reporting & Cooperative Cancellation**:
   - Long-running loops emit periodic progress percentages ($0-100\%$) and check a cancellation token at each iteration.
4. **Execution Isolation**: Strategy calculations run inside isolated worker threads or worker subprocesses, decoupled from web request handling.

## Consequences
- Fast API response times ($< 50\text{ms}$) with immediate `202 Accepted` returns.
- Full real-time observability of long-running research tasks in the frontend.
- Zero external broker requirements for single-node local installations while retaining a clean interface for Redis-backed distributed scaling.
