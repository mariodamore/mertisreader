__all__ = ['LazyArray', 'LazyCSVLoader']

import numpy as np
from typing import Optional


class LazyArray:
    """
    Lazy-loading proxy for FITS data arrays using memmap.

    Per ADR-006:
    - Defer I/O via astropy.io.fits.open(..., memmap=True)
    - .shape, .dtype, .header never trigger I/O
    - Safe: slicing, iteration, .mean(), .sum()
    - Unsafe (raise NotImplementedError): fancy indexing, reshape, transpose
    - .materialize() forces full load into RAM
    """

    def __init__(self, fits_data, header: Optional[dict] = None, hdu=None):
        self._fits_data = fits_data
        self._header = header or {}
        self._hdu = hdu
        self._materialized = False
        self._materialized_array = None

    @property
    def shape(self):
        """Array shape. No I/O triggered."""
        return self._fits_data.shape

    @property
    def dtype(self):
        """Array data type. No I/O triggered."""
        return self._fits_data.dtype

    @property
    def ndim(self):
        """Number of dimensions. No I/O triggered."""
        return self._fits_data.ndim

    @property
    def size(self):
        """Total number of elements. No I/O triggered."""
        return self._fits_data.size

    @property
    def header(self):
        """FITS header. No I/O triggered."""
        return self._header

    @property
    def materialized(self):
        """Whether array has been materialized into RAM."""
        return self._materialized

    def materialize(self) -> np.ndarray:
        """Force full array load into RAM and return a copy."""
        if self._materialized and self._materialized_array is not None:
            return self._materialized_array.copy()
        if isinstance(self._fits_data, np.memmap):
            self._materialized_array = np.array(self._fits_data)
        else:
            self._materialized_array = self._fits_data.copy()
        self._materialized = True
        return self._materialized_array.copy()

    def __getitem__(self, key):
        # Check for fancy indexing
        if isinstance(key, (list, np.ndarray)):
            raise NotImplementedError(
                f"Fancy indexing requires materialization. Call .materialize() first."
            )
        if isinstance(key, tuple):
            for k in key:
                if isinstance(k, (list, np.ndarray)):
                    raise NotImplementedError(
                        f"Fancy indexing requires materialization. Call .materialize() first."
                    )
        return self._fits_data[key]

    def __setitem__(self, key, value):
        """Array assignment - works on memmap data."""
        self._fits_data[key] = value

    def __iter__(self):
        """Iterate over the first axis - works on memmap data."""
        for i in range(len(self._fits_data)):
            yield self._fits_data[i]

    def __len__(self):
        """Length of first axis. No I/O triggered."""
        return len(self._fits_data)

    def mean(self, axis=None, dtype=None, out=None):
        """Compute mean - works on memmap data without full load."""
        return np.mean(self._fits_data, axis=axis, dtype=dtype, out=out)

    def sum(self, axis=None, dtype=None, out=None):
        """Compute sum - works on memmap data without full load."""
        return np.sum(self._fits_data, axis=axis, dtype=dtype, out=out)

    def std(self, axis=None, dtype=None, out=None):
        """Compute standard deviation - works on memmap data."""
        return np.std(self._fits_data, axis=axis, dtype=dtype, out=out)

    def min(self, axis=None, dtype=None, out=None):
        """Compute minimum - works on memmap data."""
        return np.min(self._fits_data, axis=axis, dtype=dtype, out=out)

    def max(self, axis=None, dtype=None, out=None):
        """Compute maximum - works on memmap data."""
        return np.max(self._fits_data, axis=axis, dtype=dtype, out=out)

    def astype(self, dtype):
        """Cast array to specified dtype - works on memmap data."""
        casted = self._fits_data.astype(dtype)
        if hasattr(casted, 'shape'):
            new_lazy = LazyArray(casted, self._header.copy())
            new_lazy._materialized = True
            new_lazy._materialized_array = casted
            return new_lazy
        return casted

    def copy(self):
        """Create a copy of the array - triggers materialization."""
        return self.materialize()

    def reshape(self, *args, **kwargs):
        """Reshape array - requires materialization."""
        raise NotImplementedError(
            "Reshaping requires materialization. Call .materialize().reshape() instead"
        )

    def flatten(self):
        """Flatten array - requires materialization."""
        raise NotImplementedError(
            "Flattening requires materialization. Call .materialize().flatten() instead"
        )

    def ravel(self):
        """Flatten array - requires materialization."""
        raise NotImplementedError(
            "Raveling requires materialization. Call .materialize().ravel() instead"
        )

    def transpose(self, *args):
        """Transpose array - requires materialization."""
        raise NotImplementedError(
            "Transposing requires materialization. Call .materialize().transpose() instead"
        )

    def swapaxes(self, axis1, axis2):
        """Swap axes - requires materialization."""
        raise NotImplementedError(
            "Swapping axes requires materialization. Call .materialize().swapaxes() instead"
        )

    def __array__(self, dtype=None, copy=None):
        """Convert to numpy array - triggers materialization."""
        if copy is False:
            if dtype is None:
                return np.asarray(self._fits_data)
            return np.asarray(self._fits_data, dtype=dtype)
        if dtype is None:
            return np.array(self._fits_data)
        return np.array(self._fits_data, dtype=dtype)

    def __repr__(self):
        status = "materialized" if self._materialized else "lazy (memmap)"
        return f"LazyArray(shape={self.shape}, dtype={self.dtype}, status={status})"

    def __str__(self):
        return self.__repr__()

import polars as pl
import pandas as pd
from pathlib import Path


class LazyCSVLoader:
    """
    Lazy CSV loader using Polars scan_csv.

    Per ADR-006:
    - Uses polars.scan_csv() for unevaluated query plan
    - .materialize() calls .collect() to return DataFrame
    - Falls back to pandas DataFrame when materialized
    """

    def __init__(self, csv_path: Path, columns: list = None):
        """
        Initialize LazyCSVLoader.

        Args:
            csv_path: Path to the CSV file
            columns: Optional list of columns to select (lazy projection)
        """
        self._csv_path = Path(csv_path)
        self._columns = columns
        self._lazyframe = None
        self._materialized = False
        self._materialized_df = None

    def _ensure_lazy(self):
        """Ensure lazy frame is created."""
        if self._lazyframe is None:
            try:
                if self._columns:
                    self._lazyframe = pl.scan_csv(
                        self._csv_path,
                        has_header=False,
                        new_columns=self._columns,
                    )
                else:
                    self._lazyframe = pl.scan_csv(self._csv_path, has_header=False)
            except pl.exceptions.NoDataError:
                if self._columns:
                    empty_df = pl.DataFrame({col: [] for col in self._columns})
                    self._lazyframe = empty_df.lazy()
                else:
                    raise
            if self._columns:
                self._lazyframe = self._lazyframe.select(self._columns)

    @property
    def columns(self):
        """Column names. Creates lazy plan but does not load data."""
        self._ensure_lazy()
        return self._lazyframe.collect_schema().names()

    @property
    def shape(self):
        """Shape estimate. Creates lazy plan but does not load data."""
        self._ensure_lazy()
        return self._lazyframe.shape

    def materialize(self) -> pd.DataFrame:
        """Force full CSV load and return as pandas DataFrame."""
        if self._materialized and self._materialized_df is not None:
            return self._materialized_df.copy()

        self._ensure_lazy()
        self._materialized_df = self._lazyframe.collect().to_pandas()
        self._materialized = True
        return self._materialized_df.copy()

    def __getitem__(self, key):
        """Column or row access via lazy frame."""
        self._ensure_lazy()
        return self._lazyframe[key]

    def filter(self, *args, **kwargs):
        """Add lazy filter condition."""
        self._ensure_lazy()
        self._lazyframe = self._lazyframe.filter(*args, **kwargs)
        return self

    def select(self, *args):
        """Add lazy column selection."""
        self._ensure_lazy()
        self._lazyframe = self._lazyframe.select(*args)
        return self

    def with_columns(self, *args, **kwargs):
        """Add lazy column computation."""
        self._ensure_lazy()
        self._lazyframe = self._lazyframe.with_columns(*args, **kwargs)
        return self

    def head(self, n=10):
        """Add lazy head operation."""
        self._ensure_lazy()
        self._lazyframe = self._lazyframe.head(n)
        return self

    def tail(self, n=10):
        """Add lazy tail operation."""
        self._ensure_lazy()
        self._lazyframe = self._lazyframe.tail(n)
        return self

    def __repr__(self):
        status = "materialized" if self._materialized else "lazy (query plan)"
        return f"LazyCSVLoader(path={self._csv_path}, status={status})"

    def __str__(self):
        return self.__repr__()

# Convenience re-exports for lazy loading module
__all__ = ['LazyArray', 'LazyCSVLoader']
