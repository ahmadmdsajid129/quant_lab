from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class BaseStrategy(ABC):
    """
    Abstract Base Strategy Interface.
    Enforces that signals s_t generated from information <= t are traded at bar t+1 Open.
    """
    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        self.parameters = parameters or {}

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Compute signal series s_t in range [-1.0, 1.0] representing target position or direction.
        +1.0 = 100% Long, -1.0 = 100% Short, 0.0 = Flat.
        MUST NOT USE FUTURE LOOK-AHEAD DATA.
        """
        pass
