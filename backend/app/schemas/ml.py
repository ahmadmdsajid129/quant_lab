from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class MLTrainRequest(BaseModel):
    dataset_id: str
    model_type: str = Field(default="GBDT", description="Model family: RIDGE, RANDOM_FOREST, GBDT")
    train_ratio: float = Field(default=0.75, ge=0.5, le=0.95, description="Chronological train split ratio")
    features_selected: Optional[List[str]] = Field(default=None, description="Optional subset of features to include")


class MLMetrics(BaseModel):
    accuracy_train: float
    accuracy_test: float
    roc_auc_test: float
    brier_score: float


class MLDriftFeature(BaseModel):
    ks_statistic: float
    p_value: float
    has_drift: bool


class MLDriftSummary(BaseModel):
    drifting_features_count: int
    total_features: int
    feature_diagnostics: Dict[str, MLDriftFeature]


class MLTrainResponse(BaseModel):
    model_type: str
    n_train_samples: int
    n_test_samples: int
    metrics: MLMetrics
    feature_importances: Dict[str, float]
    concept_drift: MLDriftSummary
