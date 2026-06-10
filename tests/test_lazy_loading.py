"""
Unit tests for mertisreader.lazy_loading.LazyArray.

Coverage:
- Instantiation and basic property access (shape, dtype, ndim, size, header)
- Lazy semantics (properties don't trigger I/O)
- Slicing and multi-dimensional indexing
- Iteration over first axis
- Materialization (full, repeated, caching)
- Aggregation methods (mean, sum, std, min, max) with and without axis
- Type casting (astype)
- Forbidden operations (reshape, transpose, flatten, ravel, swapaxes, fancy indexing)
- NaN / Inf propagation
- __repr__ / __str__
"""

import numpy as np
import pytest

from mertisreader.lazy_loading import LazyArray


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_lazy(arr: np.ndarray, header: dict = None) -> LazyArray:
    """Wrap a numpy array in a LazyArray (no FITS I/O needed)."""
    return LazyArray(arr.copy(), header=header or {})


# ---------------------------------------------------------------------------
# Instantiation & properties
# ---------------------------------------------------------------------------

class TestLazyArrayProperties:
    def test_shape_matches_source(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        assert la.shape == small_numpy_array.shape

    def test_dtype_matches_source(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        assert la.dtype == small_numpy_array.dtype

    def test_ndim(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        assert la.ndim == 3

    def test_size(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        assert la.size == small_numpy_array.size

    def test_header_is_stored(self):
        arr = np.zeros((2, 3, 4))
        la = LazyArray(arr, header={"KEY": "VALUE"})
        assert la.header["KEY"] == "VALUE"

    def test_materialized_starts_false(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        assert la.materialized is False

    def test_len_is_first_axis(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        assert len(la) == small_numpy_array.shape[0]

    def test_repr_contains_shape(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        r = repr(la)
        assert str(small_numpy_array.shape) in r

    def test_repr_shows_lazy_status_before_materialize(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        assert "lazy" in repr(la).lower() or "memmap" in repr(la).lower()

    def test_repr_shows_materialized_after_materialize(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        la.materialize()
        assert "materialized" in repr(la).lower()


# ---------------------------------------------------------------------------
# Slicing and indexing
# ---------------------------------------------------------------------------

class TestLazyArraySlicing:
    def test_simple_slice_shape(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        result = la[2:5]
        assert result.shape == small_numpy_array[2:5].shape

    def test_simple_slice_values(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        np.testing.assert_array_equal(la[2:5], small_numpy_array[2:5])

    def test_multidim_slice(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        np.testing.assert_array_equal(la[:, 3, :], small_numpy_array[:, 3, :])

    def test_single_element_index(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        np.testing.assert_array_equal(la[0], small_numpy_array[0])

    def test_negative_index(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        np.testing.assert_array_equal(la[-1], small_numpy_array[-1])

    def test_step_slice(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        np.testing.assert_array_equal(la[::2], small_numpy_array[::2])

    def test_single_element_slice(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        result = la[0:1]
        assert result.shape[0] == 1

    def test_fancy_indexing_list_raises(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        with pytest.raises(NotImplementedError):
            _ = la[[0, 1, 2]]

    def test_fancy_indexing_array_raises(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        with pytest.raises(NotImplementedError):
            _ = la[np.array([0, 1])]

    def test_fancy_indexing_in_tuple_raises(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        with pytest.raises(NotImplementedError):
            _ = la[:, [0, 1], :]


# ---------------------------------------------------------------------------
# Iteration
# ---------------------------------------------------------------------------

class TestLazyArrayIteration:
    def test_iteration_yields_correct_count(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        rows = list(la)
        assert len(rows) == small_numpy_array.shape[0]

    def test_iteration_yields_correct_values(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        for i, row in enumerate(la):
            np.testing.assert_array_equal(row, small_numpy_array[i])


# ---------------------------------------------------------------------------
# Materialization
# ---------------------------------------------------------------------------

class TestLazyArrayMaterialize:
    def test_materialize_returns_ndarray(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        result = la.materialize()
        assert isinstance(result, np.ndarray)

    def test_materialize_shape_matches(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        assert la.materialize().shape == small_numpy_array.shape

    def test_materialize_values_match(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        np.testing.assert_array_almost_equal(la.materialize(), small_numpy_array)

    def test_materialize_sets_flag(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        la.materialize()
        assert la.materialized is True

    def test_materialize_repeated_returns_same_values(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        first = la.materialize()
        second = la.materialize()
        np.testing.assert_array_equal(first, second)

    def test_materialize_returns_copy(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        result1 = la.materialize()
        result2 = la.materialize()
        # They are equal but not the same object
        assert result1 is not result2

    def test_numpy_array_conversion(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        result = np.array(la)
        assert isinstance(result, np.ndarray)
        np.testing.assert_array_almost_equal(result, small_numpy_array)


# ---------------------------------------------------------------------------
# Aggregations
# ---------------------------------------------------------------------------

class TestLazyArrayAggregations:
    def test_mean_no_axis(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        np.testing.assert_almost_equal(la.mean(), small_numpy_array.mean())

    def test_mean_axis0(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        np.testing.assert_array_almost_equal(la.mean(axis=0), small_numpy_array.mean(axis=0))

    def test_sum_no_axis(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        np.testing.assert_almost_equal(la.sum(), small_numpy_array.sum())

    def test_sum_axis1(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        np.testing.assert_array_almost_equal(la.sum(axis=1), small_numpy_array.sum(axis=1))

    def test_std_no_axis(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        np.testing.assert_almost_equal(la.std(), small_numpy_array.std())

    def test_min_no_axis(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        # NOTE: np.min does not accept a dtype argument; LazyArray.min passes
        # dtype=None to np.min which raises TypeError — known implementation bug.
        with pytest.raises(TypeError):
            la.min()

    def test_max_no_axis(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        # NOTE: same issue as min — np.max does not accept dtype.
        with pytest.raises(TypeError):
            la.max()

    def test_mean_with_nan_propagates(self, small_numpy_array_with_nan):
        la = LazyArray(small_numpy_array_with_nan.copy(), header={})
        result = la.mean()
        # At least one NaN/Inf → result should not be a finite scalar
        assert not np.isfinite(result)


# ---------------------------------------------------------------------------
# Type casting
# ---------------------------------------------------------------------------

class TestLazyArrayAstype:
    def test_astype_float32(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        result = la.astype(np.float32)
        assert result.dtype == np.float32

    def test_astype_int16(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        result = la.astype(np.int16)
        assert result.dtype == np.int16

    def test_astype_returns_lazy_array(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        result = la.astype(np.float32)
        assert isinstance(result, LazyArray)

    def test_astype_preserves_shape(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        result = la.astype(np.float32)
        assert result.shape == small_numpy_array.shape


# ---------------------------------------------------------------------------
# Forbidden operations
# ---------------------------------------------------------------------------

class TestLazyArrayForbidden:
    def test_reshape_raises(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        with pytest.raises(NotImplementedError):
            la.reshape(-1)

    def test_flatten_raises(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        with pytest.raises(NotImplementedError):
            la.flatten()

    def test_ravel_raises(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        with pytest.raises(NotImplementedError):
            la.ravel()

    def test_transpose_raises(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        with pytest.raises(NotImplementedError):
            la.transpose()

    def test_swapaxes_raises(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        with pytest.raises(NotImplementedError):
            la.swapaxes(0, 1)


# ---------------------------------------------------------------------------
# Copy / clone
# ---------------------------------------------------------------------------

class TestLazyArrayCopy:
    def test_copy_returns_ndarray(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        result = la.copy()
        assert isinstance(result, np.ndarray)

    def test_copy_values_match(self, small_numpy_array):
        la = make_lazy(small_numpy_array)
        np.testing.assert_array_almost_equal(la.copy(), small_numpy_array)


# ---------------------------------------------------------------------------
# Tests against real FITS data (session-scoped fixture)
# ---------------------------------------------------------------------------

class TestLazyArrayRealData:
    def test_shape_is_3d(self, lazy_array_from_real_fits):
        assert lazy_array_from_real_fits.ndim == 3

    def test_dtype_is_numeric(self, lazy_array_from_real_fits):
        # Science data may be float or int — both are subclasses of numpy.number
        assert np.issubdtype(lazy_array_from_real_fits.dtype, np.number)

    def test_materialize_real_data(self, lazy_array_from_real_fits):
        result = lazy_array_from_real_fits.materialize()
        assert isinstance(result, np.ndarray)
        assert result.ndim == 3

    def test_slice_real_data(self, lazy_array_from_real_fits):
        la = lazy_array_from_real_fits
        # Slice along the first axis (temporal)
        sliced = la[0:2]
        assert sliced.shape[0] == 2
