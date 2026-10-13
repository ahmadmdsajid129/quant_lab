import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
import pandas as pd
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Dataset, Workspace
from app.engine.data.synthetic import generate_synthetic_ohlcv
from app.engine.data.quality import run_data_quality_audit


class DataService:
    @staticmethod
    def get_parquet_path(dataset_id: str) -> Path:
        base_dir = Path(settings.PARQUET_STORAGE_PATH)
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir / f"{dataset_id}.parquet"

    @classmethod
    def save_and_register_dataset(
        cls,
        db: Session,
        workspace_id: str,
        symbol: str,
        name: str,
        source: str,
        df: pd.DataFrame,
        timeframe: str = "1d",
    ) -> Dataset:
        """
        Audit data quality, write to columnar Parquet, and register in database catalog.
        """
        dataset_id = str(uuid.uuid4())
        parquet_file = cls.get_parquet_path(dataset_id)
        
        # Ensure timestamp is datetime and sort chronologically
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

        # Run 5-point data quality audit
        audit_results = run_data_quality_audit(df)

        # Write to columnar Parquet
        df.to_parquet(parquet_file, engine="pyarrow", index=False)

        start_date = df["timestamp"].iloc[0]
        end_date = df["timestamp"].iloc[-1]
        total_bars = len(df)

        dataset = Dataset(
            id=dataset_id,
            workspace_id=workspace_id,
            symbol=symbol.upper(),
            name=name,
            source=source.upper(),
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            total_bars=total_bars,
            parquet_path=str(parquet_file.relative_to(Path.cwd()) if parquet_file.is_relative_to(Path.cwd()) else parquet_file),
            quality_score=audit_results["score"],
            quality_audit=audit_results,
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

    @classmethod
    def load_ohlcv(
        cls,
        dataset: Dataset,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Load columnar Parquet file with date filtering.
        """
        parquet_file = cls.get_parquet_path(dataset.id)
        if not parquet_file.exists():
            raise FileNotFoundError(f"Parquet file not found for dataset {dataset.id}")
        
        df = pd.read_parquet(parquet_file, engine="pyarrow")
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        if start_date:
            df = df[df["timestamp"] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df["timestamp"] <= pd.to_datetime(end_date)]
        if limit:
            df = df.iloc[-limit:]

        return df.reset_index(drop=True)

    @classmethod
    def create_synthetic_dataset(
        cls,
        db: Session,
        workspace_id: str,
        symbol: str = "SYNTH-EQ",
        periods: int = 504,  # ~2 years
        initial_price: float = 100.0,
        annual_drift: float = 0.08,
        annual_volatility: float = 0.20,
        seed: int = 42,
    ) -> Dataset:
        """Generate and register deterministic synthetic market dataset."""
        df = generate_synthetic_ohlcv(
            symbol=symbol,
            periods=periods,
            initial_price=initial_price,
            annual_drift=annual_drift,
            annual_volatility=annual_volatility,
            seed=seed,
        )
        name = f"Synthetic {symbol} (Seed {seed})"
        return cls.save_and_register_dataset(
            db=db,
            workspace_id=workspace_id,
            symbol=symbol,
            name=name,
            source="SYNTHETIC",
            df=df,
        )
