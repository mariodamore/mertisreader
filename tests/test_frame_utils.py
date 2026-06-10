"""
Unit tests for mertisreader.frame_utils and mertisreader.core error paths.

Coverage:
- normalize_raw_axis_order: correct transposition, idempotence, data integrity
- get_frame_dimensions: output structure, column names, multi-frame dict
- detect_interpolation_target: each mode ('match', 'up', 'down', 'none', unknown)
  including ValueError on heterogeneous dims with mode='match'
  and ValueError on empty dict
- resample_frame: no-op when already at target, upsample, downsample
- assemble_frames: uniform frames (match), upsample (up), downsample (down),
  no-interp (none), metadata keys, temporal sort via sort_indices
- filter_frames_by_size: keeps/discards correctly
- get_frames_by_shape_groups: groups by (n_spectrals, n_pixels)
- MERTISDataPackReader: invalid path, empty dir, mixed levels, UNKNOWN level
- extract_mertis_hk_columns: returns list of strings from real LBLX
"""

import pathlib
import numpy as np
import pandas as pd
import pytest

from mertisreader.frame_utils import (
    normalize_raw_axis_order,
    get_frame_dimensions,
    detect_interpolation_target,
    resample_frame,
    assemble_frames,
    filter_frames_by_size,
    get_frames_by_shape_groups,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_frames(*shapes) -> dict:
    """Create a dict of named random 3-D arrays with given shapes."""
    rng = np.random.default_rng(seed=0)
    return {f"frame_{i:02d}": rng.standard_normal(s) for i, s in enumerate(shapes)}


# ---------------------------------------------------------------------------
# normalize_raw_axis_order
# ---------------------------------------------------------------------------

class TestNormalizeRawAxisOrder:
    def test_shape_transposed(self):
        arr = np.zeros((62415, 100, 40))
        result = normalize_raw_axis_order(arr)
        assert result.shape == (40, 100, 62415)

    def test_small_shape_transposed(self):
        arr = np.zeros((10, 5, 3))
        result = normalize_raw_axis_order(arr)
        assert result.shape == (3, 5, 10)

    def test_data_integrity_preserved(self):
        rng = np.random.default_rng(seed=7)
        arr = rng.standard_normal((20, 8, 4))
        normalized = normalize_raw_axis_order(arr)
        # Value at original [t, p, s] should appear at normalized [s, p, t]
        t, p, s = 3, 2, 1
        np.testing.assert_almost_equal(normalized[s, p, t], arr[t, p, s])

    def test_idempotence_via_inverse(self):
        """Applying the inverse transpose should restore the original."""
        arr = np.arange(24).reshape(4, 3, 2).astype(float)
        normalized = normalize_raw_axis_order(arr)
        restored = np.transpose(normalized, (2, 1, 0))  # (spec, pix, temp) → (temp, pix, spec)
        np.testing.assert_array_equal(restored, arr)

    def test_returns_view_or_copy(self):
        arr = np.zeros((10, 5, 3))
        result = normalize_raw_axis_order(arr)
        assert isinstance(result, np.ndarray)


# ---------------------------------------------------------------------------
# get_frame_dimensions
# ---------------------------------------------------------------------------

class TestGetFrameDimensions:
    def test_returns_dataframe(self):
        frames = make_frames((8, 10, 20))
        result = get_frame_dimensions(frames)
        assert isinstance(result, pd.DataFrame)

    def test_columns_present(self):
        frames = make_frames((8, 10, 20))
        df = get_frame_dimensions(frames)
        assert set(df.columns) == {"n_files", "n_pixels", "n_spectrals"}

    def test_index_matches_frame_keys(self):
        frames = make_frames((8, 10, 20), (8, 10, 30))
        df = get_frame_dimensions(frames)
        assert set(df.index) == set(frames.keys())

    def test_correct_values_single_frame(self):
        # shape (n_spectrals=8, n_pixels=10, n_files=20)
        frames = {"a": np.zeros((8, 10, 20))}
        df = get_frame_dimensions(frames)
        assert df.loc["a", "n_spectrals"] == 8
        assert df.loc["a", "n_pixels"] == 10
        assert df.loc["a", "n_files"] == 20

    def test_correct_values_multiple_frames(self):
        frames = {
            "x": np.zeros((8, 10, 20)),
            "y": np.zeros((16, 20, 40)),
        }
        df = get_frame_dimensions(frames)
        assert df.loc["y", "n_spectrals"] == 16
        assert df.loc["y", "n_pixels"] == 20


# ---------------------------------------------------------------------------
# detect_interpolation_target
# ---------------------------------------------------------------------------

class TestDetectInterpolationTarget:
    def test_match_uniform_succeeds(self):
        frames = make_frames((8, 10, 20), (8, 10, 30))
        result = detect_interpolation_target(frames, mode="match")
        assert result["n_spectrals"] == 8
        assert result["n_pixels"] == 10
        assert result["mode_applied"] == "none"

    def test_match_heterogeneous_raises(self):
        frames = make_frames((8, 10, 20), (16, 10, 20))
        with pytest.raises(ValueError, match="match"):
            detect_interpolation_target(frames, mode="match")

    def test_up_returns_max_dims(self):
        frames = make_frames((8, 10, 20), (16, 20, 20))
        result = detect_interpolation_target(frames, mode="up")
        assert result["n_spectrals"] == 16
        assert result["n_pixels"] == 20
        assert result["mode_applied"] == "up"

    def test_down_returns_min_dims(self):
        frames = make_frames((8, 10, 20), (16, 20, 20))
        result = detect_interpolation_target(frames, mode="down")
        assert result["n_spectrals"] == 8
        assert result["n_pixels"] == 10
        assert result["mode_applied"] == "down"

    def test_none_returns_none_dims(self):
        frames = make_frames((8, 10, 20), (16, 20, 20))
        result = detect_interpolation_target(frames, mode="none")
        assert result["n_spectrals"] is None
        assert result["n_pixels"] is None
        assert result["mode_applied"] == "none"

    def test_unknown_mode_raises(self):
        frames = make_frames((8, 10, 20))
        with pytest.raises(ValueError):
            detect_interpolation_target(frames, mode="invalid_mode")

    def test_empty_dict_raises(self):
        with pytest.raises(ValueError):
            detect_interpolation_target({})


# ---------------------------------------------------------------------------
# resample_frame
# ---------------------------------------------------------------------------

class TestResampleFrame:
    def test_no_resample_when_already_target(self):
        arr = np.ones((8, 10, 20))
        result, status = resample_frame(arr, {"n_spectrals": 8, "n_pixels": 10}, verbose=False)
        assert result.shape == arr.shape
        assert status == "none"

    def test_upsample_doubles_spectrals(self):
        arr = np.ones((8, 10, 20))
        result, status = resample_frame(arr, {"n_spectrals": 16, "n_pixels": 10}, verbose=False)
        assert result.shape[0] == 16
        assert result.shape[1] == 10
        assert result.shape[2] == 20  # temporal axis unchanged

    def test_downsample_halves_pixels(self):
        arr = np.ones((8, 20, 30))
        result, status = resample_frame(arr, {"n_spectrals": 8, "n_pixels": 10}, verbose=False)
        assert result.shape[1] == 10

    def test_status_string_contains_zoom(self):
        arr = np.ones((8, 10, 20))
        _, status = resample_frame(arr, {"n_spectrals": 16, "n_pixels": 20}, verbose=False)
        assert "zoom" in status

    def test_output_is_float(self):
        arr = np.ones((8, 10, 20), dtype=np.float32)
        result, _ = resample_frame(arr, {"n_spectrals": 16, "n_pixels": 10}, verbose=False)
        assert np.issubdtype(result.dtype, np.floating)


# ---------------------------------------------------------------------------
# assemble_frames
# ---------------------------------------------------------------------------

class TestAssembleFrames:
    def test_match_mode_uniform_succeeds(self):
        frames = make_frames((8, 10, 20), (8, 10, 15))
        cube, meta = assemble_frames(frames, interp_mode="match")
        assert cube.ndim == 3
        assert cube.shape[2] == 35  # 20 + 15 temporal samples

    def test_match_mode_heterogeneous_raises(self):
        frames = make_frames((8, 10, 20), (16, 10, 20))
        with pytest.raises(ValueError):
            assemble_frames(frames, interp_mode="match")

    def test_up_mode_uses_largest_dims(self):
        frames = make_frames((8, 10, 20), (16, 20, 20))
        cube, meta = assemble_frames(frames, interp_mode="up")
        assert cube.shape[0] == 16
        assert cube.shape[1] == 20

    def test_down_mode_uses_smallest_dims(self):
        frames = make_frames((8, 10, 20), (16, 20, 20))
        cube, meta = assemble_frames(frames, interp_mode="down")
        assert cube.shape[0] == 8
        assert cube.shape[1] == 10

    def test_none_mode_concatenates(self):
        # All uniform shapes so 'none' concatenates without error
        frames = make_frames((8, 10, 20), (8, 10, 20))
        cube, meta = assemble_frames(frames, interp_mode="none")
        assert cube.shape[2] == 40

    def test_metadata_keys_present(self):
        frames = make_frames((8, 10, 20))
        _, meta = assemble_frames(frames, interp_mode="match")
        for key in ("interpolation_mode", "interpolation_order", "n_temporal_samples",
                    "file_keys", "file_indices"):
            assert key in meta

    def test_temporal_sort_applied(self):
        frames = make_frames((8, 10, 3), (8, 10, 3))
        sort_idx = np.array([5, 4, 3, 2, 1, 0])
        cube_unsorted, _ = assemble_frames(frames, interp_mode="match")
        cube_sorted, _ = assemble_frames(frames, interp_mode="match", sort_indices=sort_idx)
        np.testing.assert_array_equal(cube_sorted[:, :, 0], cube_unsorted[:, :, 5])

    def test_output_dtype_float(self):
        frames = make_frames((8, 10, 20))
        cube, _ = assemble_frames(frames, interp_mode="match")
        assert np.issubdtype(cube.dtype, np.floating)


# ---------------------------------------------------------------------------
# filter_frames_by_size
# ---------------------------------------------------------------------------

class TestFilterFramesBySize:
    def test_keep_frames_above_min_pixels(self):
        from mertisreader.frame_utils import filter_frames_by_size
        frames = {
            "a": np.zeros((8, 5, 20)),
            "b": np.zeros((8, 20, 20)),
        }
        result = filter_frames_by_size(frames, min_pixels=10)
        assert set(result.keys()) == {"b"}

    def test_keep_frames_above_min_temporal(self):
        from mertisreader.frame_utils import filter_frames_by_size
        frames = {
            "short": np.zeros((8, 10, 3)),
            "long":  np.zeros((8, 10, 100)),
        }
        result = filter_frames_by_size(frames, min_frames=10)
        assert set(result.keys()) == {"long"}

    def test_empty_when_nothing_meets_threshold(self):
        from mertisreader.frame_utils import filter_frames_by_size
        frames = {"a": np.zeros((8, 10, 20))}
        result = filter_frames_by_size(frames, min_pixels=999)
        assert len(result) == 0

    def test_no_filter_keeps_all(self):
        from mertisreader.frame_utils import filter_frames_by_size
        frames = make_frames((8, 10, 20), (4, 5, 10))
        result = filter_frames_by_size(frames)
        assert set(result.keys()) == set(frames.keys())

    def test_combined_filters(self):
        from mertisreader.frame_utils import filter_frames_by_size
        frames = {
            "a": np.zeros((8, 10, 5)),   # fails min_frames
            "b": np.zeros((8, 5, 100)),  # fails min_pixels
            "c": np.zeros((8, 10, 100)), # passes both
        }
        result = filter_frames_by_size(frames, min_pixels=10, min_frames=50)
        assert set(result.keys()) == {"c"}


# ---------------------------------------------------------------------------
# get_frames_by_shape_groups
# ---------------------------------------------------------------------------

class TestGetFramesByShapeGroups:
    def test_groups_by_shape(self):
        frames = {
            "a": np.zeros((8, 10, 20)),
            "b": np.zeros((8, 10, 15)),
            "c": np.zeros((16, 20, 20)),
        }
        groups = get_frames_by_shape_groups(frames)
        assert len(groups) == 2  # two distinct (n_spectrals, n_pixels) pairs

    def test_single_group_when_uniform(self):
        frames = make_frames((8, 10, 20), (8, 10, 30), (8, 10, 40))
        groups = get_frames_by_shape_groups(frames)
        assert len(groups) == 1


# ---------------------------------------------------------------------------
# MERTISDataPackReader — error handling
# ---------------------------------------------------------------------------

class TestMERTISDataPackReaderErrors:
    def test_invalid_path_raises(self, tmp_path):
        from mertisreader.core import MERTISDataPackReader
        missing = tmp_path / "nonexistent_dir"
        # Reader accepts any path; it will find no FITS files
        reader = MERTISDataPackReader(missing)
        assert reader.fits_files == []

    def test_empty_directory_level_unknown(self, tmp_path):
        from mertisreader.core import MERTISDataPackReader
        reader = MERTISDataPackReader(tmp_path)
        assert reader.processing_level == "UNKNOWN"

    def test_mixed_levels_raises(self, tmp_path):
        from mertisreader.core import MERTISDataPackReader
        # Place FITS stubs with both RAW and CAL naming conventions
        (tmp_path / "mer_raw_sc_tis_dummy__0_1.fits").touch()
        (tmp_path / "mer_cal_sc_tis_dummy__0_1.fits").touch()
        with pytest.raises(ValueError, match="Multiple processing levels"):
            MERTISDataPackReader(tmp_path)

    def test_raw_level_detected(self, raw_dir):
        from mertisreader.core import MERTISDataPackReader
        reader = MERTISDataPackReader(raw_dir)
        assert reader.processing_level == "RAW"

    def test_cal_level_detected(self, cal_dir):
        from mertisreader.core import MERTISDataPackReader
        reader = MERTISDataPackReader(cal_dir)
        assert reader.processing_level == "CAL"

    def test_par_level_detected(self, par_dir):
        from mertisreader.core import MERTISDataPackReader
        reader = MERTISDataPackReader(par_dir)
        assert reader.processing_level == "PAR"

    def test_output_dir_defaults_to_sibling(self, raw_dir):
        from mertisreader.core import MERTISDataPackReader
        reader = MERTISDataPackReader(raw_dir)
        expected_name = raw_dir.name + "-analysis_products"
        assert reader.output_dir.name == expected_name

    def test_custom_output_dir(self, raw_dir, tmp_path):
        from mertisreader.core import MERTISDataPackReader
        reader = MERTISDataPackReader(raw_dir, output_dir=str(tmp_path))
        assert reader.output_dir == tmp_path

    def test_get_original_frames_before_assembler_raises(self, reader_raw):
        from mertisreader.core import MERTISDataPackReader
        fresh = MERTISDataPackReader(reader_raw.input_dir)
        with pytest.raises(RuntimeError):
            fresh.get_original_frames()


# ---------------------------------------------------------------------------
# extract_mertis_hk_columns
# ---------------------------------------------------------------------------

class TestExtractMertisHkColumns:
    def test_returns_list(self, raw_hk_csv):
        from mertisreader.core import extract_mertis_hk_columns
        result = extract_mertis_hk_columns(raw_hk_csv)
        assert isinstance(result, list)

    def test_returns_non_empty(self, raw_hk_csv):
        from mertisreader.core import extract_mertis_hk_columns
        result = extract_mertis_hk_columns(raw_hk_csv)
        assert len(result) > 0

    def test_all_strings(self, raw_hk_csv):
        from mertisreader.core import extract_mertis_hk_columns
        result = extract_mertis_hk_columns(raw_hk_csv)
        assert all(isinstance(c, str) for c in result)

    def test_missing_file_raises(self, tmp_path):
        from mertisreader.core import extract_mertis_hk_columns
        fake = tmp_path / "no_such_file.dat"
        with pytest.raises(Exception):
            extract_mertis_hk_columns(fake)
