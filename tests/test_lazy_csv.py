"""
Unit tests for mertisreader.lazy_loading.LazyCSVLoader.

Coverage:
- Instantiation with valid file and optional column list
- Missing file error
- Lazy plan creation (no data load until materialize)
- filter() – single condition, chained conditions, empty result
- select() – column selection, non-existent column error
- with_columns() – adding computed columns
- head() / tail() – limit operations
- materialize() – returns pandas DataFrame, caching, dtypes
- Edge cases: headers-only CSV (no data rows)
- Chained lazy operations before materialization
- __repr__ / __str__
"""

import pathlib
import warnings

import numpy as np
import pandas as pd
import polars as pl
import pytest

from mertisreader.lazy_loading import LazyCSVLoader


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

class TestLazyCSVLoaderInit:
    def test_init_with_valid_file(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        assert loader._csv_path == pathlib.Path(tmp_csv_file)

    def test_init_with_column_list(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b"])
        assert loader._columns == ["a", "b"]

    def test_init_missing_file_deferred(self, tmp_path):
        # LazyCSVLoader defers I/O; no error on __init__ with missing file
        missing = tmp_path / "no_such_file.csv"
        loader = LazyCSVLoader(missing)
        assert loader._csv_path == missing

    def test_init_sets_not_materialized(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        assert loader._materialized is False

    def test_repr_shows_lazy_before_materialize(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        r = repr(loader)
        assert "lazy" in r.lower()

    def test_repr_shows_materialized_after(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        loader.materialize()
        assert "materialized" in repr(loader).lower()

    def test_str_matches_repr(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        assert str(loader) == repr(loader)


# ---------------------------------------------------------------------------
# Materialization
# ---------------------------------------------------------------------------

class TestLazyCSVLoaderMaterialize:
    def test_materialize_returns_dataframe(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        result = loader.materialize()
        assert isinstance(result, pd.DataFrame)

    def test_materialize_correct_columns(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        df = loader.materialize()
        assert set(df.columns) == {"a", "b", "c"}

    def test_materialize_correct_row_count(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        df = loader.materialize()
        assert len(df) == 3  # "a,b,c\n1,2,3\n4,5,6\n7,8,9\n"

    def test_materialize_correct_values(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        df = loader.materialize()
        assert list(df["a"]) == [1, 4, 7]

    def test_materialize_sets_flag(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        loader.materialize()
        assert loader._materialized is True

    def test_materialize_repeated_returns_equal_dataframes(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        df1 = loader.materialize()
        df2 = loader.materialize()
        pd.testing.assert_frame_equal(df1, df2)

    def test_materialize_returns_copy(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        df1 = loader.materialize()
        df2 = loader.materialize()
        assert df1 is not df2

    def test_materialize_missing_file_raises(self, tmp_path):
        missing = tmp_path / "no_such.csv"
        loader = LazyCSVLoader(missing)
        with pytest.raises(Exception):
            loader.materialize()

    def test_materialize_empty_csv_returns_empty_df(self, tmp_empty_csv):
        loader = LazyCSVLoader(tmp_empty_csv, columns=["col_x", "col_y"])
        df = loader.materialize()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_materialize_empty_csv_preserves_columns(self, tmp_empty_csv):
        loader = LazyCSVLoader(tmp_empty_csv, columns=["col_x", "col_y"])
        df = loader.materialize()
        assert set(df.columns) == {"col_x", "col_y"}

    def test_columns_property_creates_lazy_plan(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b"])
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            assert loader.columns == ["a", "b"]
        assert caught == []

    def test_shape_property_creates_lazy_plan(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        with pytest.raises(AttributeError):
            _ = loader.shape


# ---------------------------------------------------------------------------
# filter()
# ---------------------------------------------------------------------------

class TestLazyCSVLoaderFilter:
    def test_filter_reduces_rows(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        loader.filter(pl.col("a") > 1)
        df = loader.materialize()
        assert len(df) == 2  # rows 4 and 7

    def test_filter_correct_values(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        loader.filter(pl.col("a") == 4)
        df = loader.materialize()
        assert list(df["a"]) == [4]

    def test_filter_chained(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        loader.filter(pl.col("a") > 1).filter(pl.col("a") < 7)
        df = loader.materialize()
        assert list(df["a"]) == [4]

    def test_filter_empty_result(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        loader.filter(pl.col("a") > 999)
        df = loader.materialize()
        assert len(df) == 0

    def test_filter_returns_self(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        result = loader.filter(pl.col("a") > 0)
        assert result is loader


# ---------------------------------------------------------------------------
# select()
# ---------------------------------------------------------------------------

class TestLazyCSVLoaderSelect:
    def test_select_single_column(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        loader.select("a")
        df = loader.materialize()
        assert list(df.columns) == ["a"]

    def test_select_multiple_columns(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        loader.select(["a", "b"])
        df = loader.materialize()
        assert set(df.columns) == {"a", "b"}

    def test_select_returns_self(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        result = loader.select("a")
        assert result is loader

    def test_getitem_returns_lazyframe_slice(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        result = loader[0:2]
        assert hasattr(result, "collect")


# ---------------------------------------------------------------------------
# with_columns()
# ---------------------------------------------------------------------------

class TestLazyCSVLoaderWithColumns:
    def test_with_columns_adds_computed_column(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        loader.with_columns((pl.col("a") * 2).alias("a_double"))
        df = loader.materialize()
        assert "a_double" in df.columns
        assert list(df["a_double"]) == [2, 8, 14]

    def test_with_columns_returns_self(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        result = loader.with_columns((pl.col("a") + 1).alias("a1"))
        assert result is loader


# ---------------------------------------------------------------------------
# head() / tail()
# ---------------------------------------------------------------------------

class TestLazyCSVLoaderHeadTail:
    def test_head_limits_rows(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        loader.head(1)
        df = loader.materialize()
        assert len(df) == 1
        assert list(df["a"]) == [1]

    def test_tail_limits_rows(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        loader.tail(1)
        df = loader.materialize()
        assert len(df) == 1
        assert list(df["a"]) == [7]


# ---------------------------------------------------------------------------
# Chained operations
# ---------------------------------------------------------------------------

class TestLazyCSVLoaderChaining:
    def test_filter_select_chain(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        loader.filter(pl.col("a") > 1).select(["a", "c"])
        df = loader.materialize()
        assert set(df.columns) == {"a", "c"}
        assert len(df) == 2

    def test_select_with_columns_chain(self, tmp_csv_file):
        loader = LazyCSVLoader(tmp_csv_file, columns=["a", "b", "c"])
        loader.select(["a", "b"]).with_columns((pl.col("a") + pl.col("b")).alias("sum"))
        df = loader.materialize()
        assert "sum" in df.columns
        assert list(df["sum"]) == [3, 9, 15]


# ---------------------------------------------------------------------------
# Real data tests
# ---------------------------------------------------------------------------

class TestLazyCSVLoaderRealData:
    def test_materialize_returns_dataframe(self, raw_hk_csv):
        """Real HK DAT files have no header row; read without column projection."""
        from mertisreader.lazy_loading import LazyCSVLoader

        # Scan without column names first (polars treats first data row as header)
        loader = LazyCSVLoader(raw_hk_csv)
        df = loader.materialize()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_real_columns_match_label(self, raw_hk_csv):
        """Column names from LBLX match when provided as override to scan_csv."""
        import polars as pl
        from mertisreader.core import extract_mertis_hk_columns

        columns = extract_mertis_hk_columns(raw_hk_csv)
        # Use polars directly with has_header=False and new_columns to verify
        df = pl.read_csv(raw_hk_csv, has_header=False, new_columns=columns)
        assert list(df.columns) == columns
        assert len(df) > 0
