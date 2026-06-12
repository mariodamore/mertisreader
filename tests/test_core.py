"""Core reader coverage tests.

These tests target the remaining low-level branches in mertisreader.core.
"""

import pytest

from mertisreader.core import MERTISDataPackReader


class TestCoreCoverage:
    def test_tis_science_hdu_fallback_for_unknown_level(self, tmp_path):
        reader = MERTISDataPackReader(tmp_path)
        reader.processing_level = "UNKNOWN"

        assert reader._get_tis_science_hdu_names() == [
            "MERTIS_TIS_RAW_SCIENCE_DATA",
            "MERTIS_TIS_CAL_SCIENCE_DATA",
            "MERTIS_TIS_CALIB_SCIENCE_DATA",
            "MERTIS_TIS_PAR_SCIENCE_DATA",
        ]

    def test_data_collector_skips_empty_hk_file_list(self, tmp_path):
        reader = MERTISDataPackReader(tmp_path)
        reader.input_path_dict = {"hk_default": [], "sc_tis": []}

        reader.data_collector()

        assert reader.collect_data == {}

    def test_lazy_data_collector_raises_when_science_hdu_missing(self, tmp_path, monkeypatch):
        class FakeHDUList:
            def __contains__(self, item):
                return False

        def fake_open(*args, **kwargs):
            return FakeHDUList()

        fake_file = tmp_path / "mer_raw_sc_tis_missing__0_1.fits"
        fake_file.touch()

        reader = MERTISDataPackReader(tmp_path, lazy=True)
        reader.processing_level = "RAW"
        reader.input_path_dict = {"sc_tis": [fake_file], "hk_default": []}

        monkeypatch.setattr("astropy.io.fits.open", fake_open)

        with pytest.raises(KeyError, match="No matching science HDU found"):
            reader.data_collector()

    def test_data_assembler_bootstraps_collection_when_needed(self, cal_dir):
        reader = MERTISDataPackReader(cal_dir)

        reader.data_assembler()

        assert hasattr(reader, "collect_data")
        assert len(reader.frames) > 0

    def test_data_assembler_verbose_and_unknown_level_paths(self, cal_dir, capsys):
        reader = MERTISDataPackReader(cal_dir)
        reader.data_collector()

        reader.data_assembler(verbose=True)
        captured = capsys.readouterr()
        assert "Collected data statistics:" in captured.out
        assert "Indices of measurements targets" in captured.out

        reader.processing_level = "UNKNOWN"
        with pytest.raises(ValueError, match="Unknown TIS file level"):
            reader.data_assembler()

    def test_data_assembler_uses_calib_fallback_when_primary_cal_hdu_is_missing(self, tmp_path):
        import numpy as np

        class FakeHDU:
            def __init__(self, name, data):
                self.name = name
                self.data = data

        class FakeHDUList:
            def __init__(self):
                metadata = np.array(
                    [
                        ("2026-06-12T00:00:00", "Space"),
                        ("2026-06-12T00:01:00", "BB7"),
                        ("2026-06-12T00:02:00", "BB3"),
                        ("2026-06-12T00:03:00", "Planet"),
                    ],
                    dtype=[("TIME_UTC", "U32"), ("HK_STAT_TIS_DATA_ACQ_TARGET", "U16")],
                )
                frame = np.arange(6, dtype=np.float64).reshape(2, 3)
                wavelength = np.arange(6, dtype=np.float64).reshape(2, 3) + 10.0
                geometry = np.arange(4, dtype=np.float64).reshape(2, 2)
                self.hdus = [
                    FakeHDU("PRIMARY", None),
                    FakeHDU("TABLE", metadata),
                    FakeHDU("MERTIS_TIS_CALIB_SCIENCE_DATA", frame),
                    FakeHDU("MERTIS_TIS_CALIB_SCIENCE_DATA_WAVELENGTH", wavelength),
                    FakeHDU("MERTIS_TIS_GEOMETRY_TARGET_LONGITUDE", geometry),
                ]

            def __getitem__(self, key):
                if key == 1:
                    return self.hdus[1]
                if isinstance(key, str):
                    if key == "MERTIS_TIS_CAL_SCIENCE_DATA":
                        raise KeyError(key)
                    for hdu in self.hdus:
                        if hdu.name == key:
                            return hdu
                    raise KeyError(key)
                return self.hdus[key]

            def __iter__(self):
                return iter(self.hdus)

        reader = MERTISDataPackReader(tmp_path)
        reader.processing_level = "CAL"
        reader.collect_data = {
            "tis": [
                {
                    "fits_data": FakeHDUList(),
                    "path": tmp_path / "fake_cal_tis.fits",
                }
            ]
        }

        reader.data_assembler()

        assert len(reader.frames) == 1
        frame = next(iter(reader.frames.values()))
        assert frame.shape == (2, 3)
        assert len(next(iter(reader.wavelengths.values()))) == 2
