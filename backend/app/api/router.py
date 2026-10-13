from fastapi import APIRouter
from app.api import (
    health,
    auth,
    workspaces,
    projects,
    datasets,
    analytics,
    backtests,
    validation,
    ml,
    portfolio,
    microstructure,
    options,
    copilot,
    paper_trading,
    reports,
    jobs,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(workspaces.router)
api_router.include_router(projects.router)
api_router.include_router(datasets.router)
api_router.include_router(analytics.router)
api_router.include_router(backtests.router)
api_router.include_router(validation.router)
api_router.include_router(ml.router)
api_router.include_router(portfolio.router)
api_router.include_router(microstructure.router)
api_router.include_router(options.router)
api_router.include_router(copilot.router)
api_router.include_router(paper_trading.router)
api_router.include_router(reports.router)
api_router.include_router(jobs.router)








