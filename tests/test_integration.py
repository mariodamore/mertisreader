"""
Integration tests for mertisreader using real MERTIS sample data.

These tests exercise the full reader workflow:
  data_collector() → data_assembler() → get_original_frames() / get_assembled_frames()

All three processing levels (RAW, CAL, PAR) are tested.
Tests use session-scoped reader fixtures from conftest.py; the readers are
created once per test session to avoid redundant I/O.
"""

import numpy as np
import pandas as pd
import pytest

from mertisreader.core import MERTISDataPackReader
from mertisreader.frame_utils import assemble_frames


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def collect_and_assemble(reader: MERTISDataPackReader):
    """Run collection + assembly pipeline on a reader."""
    reader.data_collector()
    reader.data_assembler()


# ---------------------------------------------------------------------------
# RAW level
# ---------------------------------------------------------------------------


class TestRAWIntegration:
    @pytest.fixture(scope="class", autouse=True)
    def collected_raw(self, reader_raw):
        """Only collect data; assembly is broken for RAW."""
        reader_raw.data_collector()

    def test_processing_level_is_raw(self, reader_raw):
        assert reader_raw.processing_level == "RAW"

    def test_fits_files_found(self, reader_raw):
        assert len(reader_raw.fits_files) > 0

    def test_collect_data_has_tis(self, reader_raw):
        assert "tis" in reader_raw.collect_data
        assert len(reader_raw.collect_data["tis"]) > 0

    def test_frames_dict_populated(self, reader_raw):
        reader_raw.data_assembler()
        assert len(reader_raw.frames) > 0

    def test_frames_are_3d(self, reader_raw):
        reader_raw.data_assembler()
        for key, arr in reader_raw.frames.items():
            assert arr.ndim == 3

    def test_frames_are_float64(self, reader_raw):
        reader_raw.data_assembler()
        for key, arr in reader_raw.frames.items():
            assert arr.dtype == np.float64

    def test_raw_axis_order_normalized(self, reader_raw):
        """Verify RAW data is transposed from (frames, pixels, spectrals) to (spectrals, pixels, frames)."""
        reader_raw.data_assembler()
        for key, arr in reader_raw.frames.items():
            n_spec, n_pix, n_temp = arr.shape
            # After normalization: spectral axis at 0, temporal axis at 2
            # For this dataset: original (22, 100, 40) -> normalized (40, 100, 22)
            assert n_spec == 40, f"Expected spectral=40, got {n_spec}"
            assert n_temp == 22, f"Expected temporal=22, got {n_temp}"
            assert n_pix == 100, f"Expected pixels=100, got {n_pix}"

    def test_get_original_frames_returns_dict(self, reader_raw):
        reader_raw.data_assembler()
        result = reader_raw.get_original_frames()
        assert isinstance(result, dict)

    def test_wavelengths_are_none_for_raw(self, reader_raw):
        reader_raw.data_assembler()
        for val in reader_raw.wavelengths.values():
            assert val is None

    def test_metadata_dataframe_populated(self, reader_raw):
        reader_raw.data_assembler()
        assert len(reader_raw.mertis_tis_metadata) > 0

    def test_no_geometry_for_raw(self, reader_raw):
        reader_raw.data_assembler()
        geom = getattr(reader_raw, "geom_ls", {})
        assert len(geom) == 0


# ---------------------------------------------------------------------------
# CAL level
# ---------------------------------------------------------------------------

class TestCALIntegration:
    @pytest.fixture(scope="class", autouse=True)
    def assembled_cal(self, reader_cal):
        collect_and_assemble(reader_cal)

    def test_processing_level_is_cal(self, reader_cal):
        assert reader_cal.processing_level == "CAL"

    def test_frames_are_3d(self, reader_cal):
        for key, arr in reader_cal.frames.items():
            assert arr.ndim == 3

    def test_wavelengths_present_for_cal(self, reader_cal):
        """CAL level should have non-None wavelength arrays."""
        for val in reader_cal.wavelengths.values():
            assert val is not None

    def test_geometry_present_for_cal(self, reader_cal):
        """CAL level provides geometry data."""
        assert hasattr(reader_cal, "geom_ls")
        assert len(reader_cal.geom_ls) > 0

    def test_metadata_has_time_utc(self, reader_cal):
        assert hasattr(reader_cal, "mertis_tis_metadata")
        for df in reader_cal.mertis_tis_metadata.values():
            assert "TIME_UTC" in df.columns

    def test_target_indices_populated(self, reader_cal):
        """space_index, bb7_index, bb3_index, planet_index should be set."""
        for attr in ("space_index", "bb7_index", "bb3_index", "planet_index"):
            assert hasattr(reader_cal, attr)


# ---------------------------------------------------------------------------
# PAR level
# ---------------------------------------------------------------------------

class TestPARIntegration:
    @pytest.fixture(scope="class", autouse=True)
    def assembled_par(self, reader_par):
        collect_and_assemble(reader_par)

    def test_processing_level_is_par(self, reader_par):
        assert reader_par.processing_level == "PAR"

    def test_frames_are_3d(self, reader_par):
        for key, arr in reader_par.frames.items():
            assert arr.ndim == 3

    def test_wavelengths_present_for_par(self, reader_par):
        for val in reader_par.wavelengths.values():
            assert val is not None

    def test_geometry_present_for_par(self, reader_par):
        assert hasattr(reader_par, "geom_ls")
        assert len(reader_par.geom_ls) > 0


# ---------------------------------------------------------------------------
# Frame assembly with interpolation modes (uses CAL reader)
# ---------------------------------------------------------------------------

class TestFrameAssemblyModes:
    @pytest.fixture(scope="class", autouse=True)
    def assembled_cal(self, reader_cal):
        collect_and_assemble(reader_cal)

    def test_get_assembled_match_mode(self, reader_cal):
        frames = reader_cal.get_original_frames()
        cube, meta = assemble_frames(frames, interp_mode="match")
        assert cube.ndim == 3
        assert meta["interpolation_mode"] in ("none",)

    def test_get_assembled_up_mode(self, reader_cal):
        frames = reader_cal.get_original_frames()
        cube, meta = assemble_frames(frames, interp_mode="up")
        assert cube.ndim == 3
        assert meta["interpolation_mode"] in ("none", "up")

    def test_get_assembled_down_mode(self, reader_cal):
        frames = reader_cal.get_original_frames()
        cube, meta = assemble_frames(frames, interp_mode="down")
        assert cube.ndim == 3
        assert meta["interpolation_mode"] in ("none", "down")

    def test_assembled_cube_is_float64(self, reader_cal):
        frames = reader_cal.get_original_frames()
        cube, _ = assemble_frames(frames, interp_mode="up")
        assert cube.dtype == np.float64


# ---------------------------------------------------------------------------
# Caching behaviour (ADR-004)
# ---------------------------------------------------------------------------

class TestCachingBehaviour:
    def test_get_original_frames_cached(self, reader_cal):
        """get_original_frames() returns the same object on second call (CAL)."""
        collect_and_assemble(reader_cal)
        frames1 = reader_cal.get_original_frames()
        frames2 = reader_cal.get_original_frames()
        assert frames1 is frames2


# ---------------------------------------------------------------------------
# HK column extraction end-to-end
# ---------------------------------------------------------------------------

class TestHKExtraction:
    def test_hk_default_loaded(self, reader_raw):
        reader_raw.data_collector()
        assert "hk_default" in reader_raw.collect_data
        hk_entries = reader_raw.collect_data["hk_default"]
        assert len(hk_entries) > 0

    def test_hk_data_is_dataframe_or_loader(self, reader_raw):
        reader_raw.data_collector()
        from mertisreader.lazy_loading import LazyCSVLoader
        for entry in reader_raw.collect_data.get("hk_default", []):
            data = entry["data"]
            assert isinstance(data, (pd.DataFrame, LazyCSVLoader))


# ---------------------------------------------------------------------------
# Lazy mode reader
# ---------------------------------------------------------------------------

class TestLazyModeIntegration:
    def test_lazy_reader_initializes(self, raw_dir):
        reader = MERTISDataPackReader(raw_dir, lazy=True)
        assert reader.lazy is True

    def test_lazy_collect_data_has_tis(self, raw_dir):
        reader = MERTISDataPackReader(raw_dir, lazy=True)
        reader.data_collector()
        assert "tis" in reader.collect_data

    def test_lazy_tis_data_is_lazy_array(self, raw_dir):
        from mertisreader.lazy_loading import LazyArray
        reader = MERTISDataPackReader(raw_dir, lazy=True)
        reader.data_collector()
        for entry in reader.collect_data.get("tis", []):
            assert isinstance(entry["fits_data"], LazyArray)

    def test_lazy_hk_data_is_lazy_csv(self, raw_dir):
        from mertisreader.lazy_loading import LazyCSVLoader
        reader = MERTISDataPackReader(raw_dir, lazy=True)
        reader.data_collector()
        for entry in reader.collect_data.get("hk_default", []):
            assert isinstance(entry["data"], LazyCSVLoader)
