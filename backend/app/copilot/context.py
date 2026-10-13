from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.db.models import Project, Hypothesis, Dataset, Experiment, ResearchNote


def assemble_workspace_research_context(db: Session, workspace_id: str) -> Dict[str, Any]:
    """
    Retrieve and format all active research artifacts in the workspace for grounded AI reasoning.
    """
    projects = db.query(Project).filter(Project.workspace_id == workspace_id).all()
    datasets = db.query(Dataset).filter(Dataset.workspace_id == workspace_id).all()
    experiments = (
        db.query(Experiment)
        .join(Project)
        .filter(Project.workspace_id == workspace_id)
        .order_by(Experiment.start_time.desc())
        .limit(10)
        .all()
    )

    context = {
        "projects_count": len(projects),
        "projects": [
            {
                "id": p.id,
                "name": p.title,
                "title": p.title,
                "asset_class": p.asset_class,
                "hypotheses": [
                    {
                        "id": h.id,
                        "statement": h.statement,
                        "mechanism": h.mechanism,
                        "falsification_criteria": h.falsification_criteria,
                        "status": h.status,
                    }
                    for h in p.hypotheses
                ],
            }
            for p in projects
        ],
        "datasets": [
            {
                "id": d.id,
                "symbol": d.symbol,
                "source": d.source,
                "total_bars": d.total_bars,
                "quality_flags": d.quality_audit.get("flags", []) if isinstance(d.quality_audit, dict) else [],
            }
            for d in datasets
        ],
        "recent_experiments": [
            {
                "id": e.id,
                "strategy_name": e.strategy.name if e.strategy else e.config.get("strategy_name", "Backtest"),
                "status": e.status,
                "metrics": e.metrics,
                "created_at": str(e.start_time),
            }
            for e in experiments
        ],
    }
    return context
