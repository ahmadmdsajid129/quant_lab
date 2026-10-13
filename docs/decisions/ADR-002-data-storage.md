# ADR-002: Dual-Tier Data Storage (Relational Metadata + Columnar Parquet)

**Status:** Accepted  
**Date:** 2026-10-13  
**Deciders:** Principal Architect, Data Engineer  

---

## Context
Financial research platforms handle two fundamentally distinct categories of data:
1. **Relational / Transactional Data**: Users, workspaces, project metadata, hypotheses, strategy parameters, experiment lineage records, audit logs.
2. **High-Frequency Market Time Series**: Millions of OHLCV bars, order book snapshots, tick trades, and indicator arrays.

Storing millions of tick or bar records inside standard relational tables causes significant database bloat, slow sequential scans, high memory overhead, and poor analytic query performance.

## Decision
We implement a dual-tier storage architecture:
1. **Relational Tier**: SQLite (zero-config local dev/offline tests) and PostgreSQL (production). Handled via SQLAlchemy 2.0 ORM and Alembic. Manages user entities, projects, experiment summaries, and audit logs.
2. **Columnar Time-Series Tier**: Apache Parquet files stored on the filesystem / object storage (`./data/parquet/{dataset_id}.parquet`).
   - Read/write via `pandas` and `pyarrow`.
   - Offers 10x-50x compression, rapid vector memory mapping, and zero relational database contention.

## Consequences
- Relational database remains lightweight and fast.
- Quantitative backtesting engines read Parquet files at multi-gigabyte-per-second memory bandwidth.
- Transparent offline capability with no complex cluster requirements.
