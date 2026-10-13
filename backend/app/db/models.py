import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    workspaces = relationship("WorkspaceMember", back_populates="user", cascade="all, delete-orphan")


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False, default="RESEARCHER")  # ADMIN | RESEARCHER | VIEWER
    created_at = Column(DateTime, default=utc_now, nullable=False)

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspaces")

    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_user"),
    )


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    asset_class = Column(String(100), nullable=False, default="EQUITIES")  # EQUITIES, CRYPTO, FX, MULTI_ASSET
    status = Column(String(50), nullable=False, default="DRAFT")  # DRAFT, IN_PROGRESS, VALIDATED, REJECTED, ARCHIVED
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    workspace = relationship("Workspace", back_populates="projects")
    hypotheses = relationship("Hypothesis", back_populates="project", cascade="all, delete-orphan")
    notes = relationship("ResearchNote", back_populates="project", cascade="all, delete-orphan")
    strategies = relationship("Strategy", back_populates="project", cascade="all, delete-orphan")
    experiments = relationship("Experiment", back_populates="project", cascade="all, delete-orphan")


class Hypothesis(Base):
    __tablename__ = "hypotheses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    statement = Column(Text, nullable=False)
    mechanism = Column(Text, nullable=False)
    predicted_outcome = Column(Text, nullable=False)
    falsification_criteria = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="UNTESTED")  # UNTESTED, SUPPORTED, FALSIFIED
    created_at = Column(DateTime, default=utc_now, nullable=False)

    project = relationship("Project", back_populates="hypotheses")


class ResearchNote(Base):
    __tablename__ = "research_notes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # Markdown
    created_at = Column(DateTime, default=utc_now, nullable=False)

    project = relationship("Project", back_populates="notes")


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    source = Column(String(50), nullable=False)  # STOOQ, SYNTHETIC, YAHOO, CSV
    timeframe = Column(String(20), nullable=False, default="1d")  # 1m, 5m, 1h, 1d
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_bars = Column(Integer, nullable=False)
    parquet_path = Column(String(512), nullable=False)
    quality_score = Column(Float, nullable=False, default=100.0)
    quality_audit = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    workspace = relationship("Workspace", back_populates="datasets")

    __table_args__ = (
        Index("idx_datasets_workspace_symbol", "workspace_id", "symbol"),
    )


class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    strategy_type = Column(String(100), nullable=False)  # BUY_AND_HOLD, MA_CROSSOVER, MOMENTUM, MEAN_REVERSION
    parameters = Column(JSON, nullable=False, default=dict)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    project = relationship("Project", back_populates="strategies")
    experiments = relationship("Experiment", back_populates="strategy")


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    strategy_id = Column(String(36), ForeignKey("strategies.id"), nullable=True, index=True)
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False, index=True)
    experiment_type = Column(String(50), nullable=False)  # BACKTEST, WALK_FORWARD, ML_TRAIN, PORTFOLIO_OPT
    config = Column(JSON, nullable=False, default=dict)
    metrics = Column(JSON, nullable=False, default=dict)
    status = Column(String(50), nullable=False, default="QUEUED")  # QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
    start_time = Column(DateTime, default=utc_now, nullable=False)
    end_time = Column(DateTime, nullable=True)
    lineage_hash = Column(String(64), nullable=False)

    project = relationship("Project", back_populates="experiments")
    strategy = relationship("Strategy", back_populates="experiments")
    trade_logs = relationship("TradeLog", back_populates="experiment", cascade="all, delete-orphan")


class TradeLog(Base):
    __tablename__ = "trade_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_id = Column(String(36), ForeignKey("experiments.id"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False)
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=False)
    side = Column(String(10), nullable=False)  # LONG | SHORT
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    gross_pnl = Column(Float, nullable=False)
    fees = Column(Float, nullable=False)
    net_pnl = Column(Float, nullable=False)
    return_pct = Column(Float, nullable=False)

    experiment = relationship("Experiment", back_populates="trade_logs")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_type = Column(String(50), nullable=False)  # BACKTEST, DATA_INGEST, ML_TRAIN, VALIDATION
    status = Column(String(50), nullable=False, default="QUEUED")  # QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
    progress = Column(Float, default=0.0, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    completed_at = Column(DateTime, nullable=True)


class PaperAccount(Base):
    __tablename__ = "paper_accounts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    initial_cash = Column(Float, nullable=False, default=100000.0)
    current_cash = Column(Float, nullable=False, default=100000.0)
    currency = Column(String(10), nullable=False, default="USD")
    created_at = Column(DateTime, default=utc_now, nullable=False)


class PaperPosition(Base):
    __tablename__ = "paper_positions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_id = Column(String(36), ForeignKey("paper_accounts.id"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False)
    side = Column(String(10), nullable=False)  # LONG | SHORT
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


class PaperOrder(Base):
    __tablename__ = "paper_orders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_id = Column(String(36), ForeignKey("paper_accounts.id"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False)
    order_type = Column(String(20), nullable=False)  # MARKET | LIMIT
    side = Column(String(10), nullable=False)  # BUY | SELL
    quantity = Column(Float, nullable=False)
    limit_price = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default="SUBMITTED")  # SUBMITTED, FILLED, REJECTED, CANCELLED
    filled_quantity = Column(Float, nullable=False, default=0.0)
    filled_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(36), nullable=False)
    details = Column(JSON, nullable=False, default=dict)
    timestamp = Column(DateTime, default=utc_now, nullable=False)
