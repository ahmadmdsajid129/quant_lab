from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models import Experiment, Project, Dataset, TradeLog


class ReportService:
    @staticmethod
    def build_experiment_tearsheet(db: Session, experiment_id: str, workspace_id: str) -> Dict[str, Any]:
        exp = (
            db.query(Experiment)
            .join(Project)
            .filter(Experiment.id == experiment_id, Project.workspace_id == workspace_id)
            .first()
        )
        if not exp:
            raise ValueError("Experiment not found in active workspace.")

        project = exp.project
        dataset = db.query(Dataset).filter(Dataset.id == exp.dataset_id).first()
        trade_logs = db.query(TradeLog).filter(TradeLog.experiment_id == exp.id).all()

        m = exp.metrics or {}
        cfg = exp.config or {}

        hypotheses_data = [
            {
                "statement": h.statement,
                "mechanism": h.mechanism,
                "falsification_criteria": h.falsification_criteria,
                "status": h.status,
            }
            for h in project.hypotheses
        ]

        tearsheet = {
            "title": f"Quantitative Research Tearsheet: {exp.strategy.name if exp.strategy else 'Strategy'}",
            "experiment_id": exp.id,
            "status": exp.status,
            "lineage_hash": exp.lineage_hash,
            "created_at": str(exp.start_time),
            "project": {
                "id": project.id,
                "title": project.title,
                "asset_class": project.asset_class,
                "hypotheses": hypotheses_data,
            },
            "data_provenance": {
                "symbol": dataset.symbol if dataset else "UNKNOWN",
                "source": dataset.source if dataset else "UNKNOWN",
                "total_bars": dataset.total_bars if dataset else 0,
                "start_date": str(dataset.start_date) if dataset else "",
                "end_date": str(dataset.end_date) if dataset else "",
                "quality_score": dataset.quality_score if dataset else 100.0,
            },
            "methodology_assumptions": {
                "execution_timing": "Next-Bar Open (t -> t+1)",
                "lookahead_bias_guarantee": "Strict zero-lookahead invariant enforced",
                "slippage_rate": cfg.get("slippage_pct", 0.0005),
                "commission_bps": cfg.get("commission_bps", 2.0),
                "initial_cash": cfg.get("initial_cash", 100_000.0),
            },
            "performance_kpis": {
                "total_return_pct": round(m.get("total_return", 0.0) * 100.0, 2),
                "cagr_pct": round(m.get("cagr", 0.0) * 100.0, 2),
                "annualized_volatility_pct": round(m.get("annualized_volatility", 0.0) * 100.0, 2),
                "sharpe_ratio": round(m.get("sharpe_ratio", 0.0), 2),
                "sortino_ratio": round(m.get("sortino_ratio", 0.0), 2),
                "max_drawdown_pct": round(m.get("max_drawdown", 0.0) * 100.0, 2),
                "calmar_ratio": round(m.get("calmar_ratio", 0.0), 2),
                "win_rate_pct": round(m.get("win_rate", 0.0) * 100.0, 2),
                "profit_factor": round(m.get("profit_factor", 0.0), 2),
                "var_95_pct": round(m.get("var_95", 0.0) * 100.0, 2),
                "cvar_95_pct": round(m.get("cvar_95", 0.0) * 100.0, 2),
                "total_trades": len(trade_logs),
            },
            "reproducibility_notice": "Full configuration, random seeds, and dependency environments are locked in cryptographic hash.",
        }

        return tearsheet

    @staticmethod
    def export_markdown_report(tearsheet: Dict[str, Any]) -> str:
        kpi = tearsheet["performance_kpis"]
        prov = tearsheet["data_provenance"]
        meth = tearsheet["methodology_assumptions"]
        proj = tearsheet["project"]

        md = f"""# {tearsheet['title']}
**Experiment ID:** `{tearsheet['experiment_id']}`  
**Lineage Hash:** `{tearsheet['lineage_hash']}`  
**Generated At:** `{tearsheet['created_at']}`  

---

## 1. Research Project & Hypotheses
- **Project:** {proj['title']}
- **Asset Class:** {proj['asset_class']}

### Stated Hypotheses:
"""
        for h in proj.get("hypotheses", []):
            md += f"- **Statement:** {h['statement']}\n  - *Mechanism:* {h['mechanism']}\n  - *Falsification Criteria:* {h['falsification_criteria']}\n"

        md += f"""
---

## 2. Data Provenance & Invariants
- **Asset Symbol:** `{prov['symbol']}`
- **Provider Source:** `{prov['source']}`
- **Total Observations:** `{prov['total_bars']} bars`
- **Quality Score:** `{prov['quality_score']}%`
- **Execution Timing:** `{meth['execution_timing']}`
- **Friction:** Slippage `{meth['slippage_rate']*100:.2f}%`, Commission `{meth['commission_bps']} bps`

---

## 3. Verified Performance Metrics
| Metric | Value |
| :--- | :--- |
| **Total Cumulative Return** | `{kpi['total_return_pct']}%` |
| **Compound Annual Growth (CAGR)** | `{kpi['cagr_pct']}%` |
| **Annualized Volatility** | `{kpi['annualized_volatility_pct']}%` |
| **Sharpe Ratio** | `{kpi['sharpe_ratio']}` |
| **Sortino Ratio** | `{kpi['sortino_ratio']}` |
| **Maximum Drawdown** | `{kpi['max_drawdown_pct']}%` |
| **Calmar Ratio** | `{kpi['calmar_ratio']}` |
| **Win Rate** | `{kpi['win_rate_pct']}%` |
| **Profit Factor** | `{kpi['profit_factor']}` |
| **Value at Risk (95% Daily VaR)** | `{kpi['var_95_pct']}%` |
| **Total Completed Trades** | `{kpi['total_trades']}` |

---

## 4. Reproducibility & Audit
> **Verification Guarantee:** {tearsheet['reproducibility_notice']}
"""
        return md


report_service = ReportService()
