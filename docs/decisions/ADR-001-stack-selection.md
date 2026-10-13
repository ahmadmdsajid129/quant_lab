# ADR-001: Technology Stack Selection (Next.js + FastAPI + Python 3.13)

**Status:** Accepted  
**Date:** 2026-10-13  
**Deciders:** Principal Architect, Full-Stack Lead  

---

## Context
QuantLab requires a modern, high-density scientific web workstation interface combined with high-performance quantitative computation capabilities (matrix manipulation, time-series analysis, numerical optimization, statistical modeling, machine learning).

## Decision
We select:
1. **Frontend**: Next.js 14+ / React / TypeScript with Tailwind CSS and Lucide icons.
   - *Rationale*: React offers the richest financial charting, table virtualization, and interactive UI ecosystem. TypeScript provides compile-time type safety. Next.js App Router provides clean routing and server component performance.
2. **Backend**: FastAPI (Python 3.13).
   - *Rationale*: Python is the undisputed standard language for quantitative finance, boasting battle-tested libraries (NumPy, pandas, SciPy, scikit-learn, statsmodels). FastAPI offers native async performance, automatic OpenAPI documentation, and strict Pydantic v2 data validation.
3. **Decoupled Architecture**: Frontend and Backend operate as decoupled services communicating via REST API and WebSockets.

## Consequences
- Clean separation of concerns between presentation and computation.
- Enables rapid unit testing of math models independently of HTTP layers.
- Supports running both locally without Docker or in containerized staging/production environments.
