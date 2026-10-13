from typing import Generator, Tuple, List
import numpy as np


class PurgedKFold:
    """
    Purged K-Fold Cross-Validation with Embargo (López de Prado, 2018).
    Prevents information leakage between train and test folds caused by
    overlapping labels or serial autocorrelation.
    """
    def __init__(self, n_splits: int = 5, embargo_pct: float = 0.01):
        if n_splits < 2:
            raise ValueError("n_splits must be at least 2")
        self.n_splits = n_splits
        self.embargo_pct = embargo_pct

    def split(self, n_samples: int) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        indices = np.arange(n_samples)
        embargo = int(np.ceil(n_samples * self.embargo_pct))
        fold_size = n_samples // self.n_splits

        for i in range(self.n_splits):
            test_start = i * fold_size
            test_end = (i + 1) * fold_size if i < self.n_splits - 1 else n_samples
            
            test_indices = indices[test_start:test_end]

            # Purge test interval and apply embargo after test interval
            embargo_end = min(n_samples, test_end + embargo)
            
            train_mask = np.ones(n_samples, dtype=bool)
            train_mask[test_start:embargo_end] = False
            
            train_indices = indices[train_mask]
            yield train_indices, test_indices
