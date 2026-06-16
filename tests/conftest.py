"""
Shared pytest fixtures for mertisreader tests.

Uses real MERTIS sample data from the data/ directory.
Synthetic data is used only for error-path and edge-case tests.
"""

import pathlib
import numpy as np
import pytest
from astropy.io import fits

# ---------------------------------------------------------------------------
# Paths to test data
# ---------------------------------------------------------------------------
DATA_DIR = pathlib.Path(__file__).parent.parent / "data"
PACK_DIR = DATA_DIR / (
    "bcmer_tm_all_START-20200409T000000_END-20200410T000000"
    "_CRE-20240717T132010-ParamEventBootSciHK-short"
)
RAW_DIR = PACK_DIR / "raw"
CAL_DIR = PACK_DIR / "cal"
PAR_DIR = PACK_DIR / "par"


# ---------------------------------------------------------------------------
# File-path fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def raw_dir():
    assert RAW_DIR.exists(), f"RAW data directory not found: {RAW_DIR}"
    return RAW_DIR


@pytest.fixture(scope="session")
def cal_dir():
    assert CAL_DIR.exists(), f"CAL data directory not found: {CAL_DIR}"
    return CAL_DIR


@pytest.fixture(scope="session")
def par_dir():
    assert PAR_DIR.exists(), f"PAR data directory not found: {PAR_DIR}"
    return PAR_DIR


@pytest.fixture(scope="session")
def raw_tis_fits(raw_dir):
    """Path to a real RAW TIS FITS file."""
    files = sorted(raw_dir.glob("mer_raw_sc_tis_*.fits"))
    assert files, "No RAW TIS FITS files found"
    return files[0]


@pytest.fixture(scope="session")
def cal_tis_fits(cal_dir):
    """Path to a real CAL TIS FITS file."""
    files = sorted(cal_dir.glob("mer_cal_sc_tis_*.fits"))
    assert files, "No CAL TIS FITS files found"
    return files[0]


@pytest.fixture(scope="session")
def raw_hk_csv(raw_dir):
    """Path to a real RAW HK default DAT file (CSV-like)."""
    files = sorted(raw_dir.glob("mer_raw_hk_default_*.dat"))
    assert files, "No RAW HK default DAT files found"
    return files[0]


@pytest.fixture(scope="session")
def raw_hk_xml(raw_hk_csv):
    """Path to the LBLX label file matching the RAW HK DAT file."""
    p = raw_hk_csv.with_suffix(".lblx")
    assert p.exists(), f"No LBLX label file found at: {p}"
    return p


# ---------------------------------------------------------------------------
# In-memory synthetic data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def small_numpy_array():
    """Small deterministic 3-D array for unit tests: (8, 10, 20)."""
    rng = np.random.default_rng(seed=42)
    return rng.standard_normal((8, 10, 20))


@pytest.fixture
def small_numpy_array_with_nan(small_numpy_array):
    """3-D array with NaN and Inf sentinel values injected."""
    arr = small_numpy_array.copy()
    arr[0, 0, 0] = np.nan
    arr[1, 1, 1] = np.inf
    arr[2, 2, 2] = -np.inf
    return arr


# ---------------------------------------------------------------------------
# LazyArray fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def lazy_array_from_real_fits(raw_tis_fits):
    """LazyArray backed by the RAW science data HDU (3D array)."""
    from mertisreader.lazy_loading import LazyArray

    # memmap=False required because BZERO/BSCALE/BLANK keywords prevent memmap
    hdulist = fits.open(str(raw_tis_fits), memmap=False)
    hdu = hdulist["MERTIS_TIS_RAW_SCIENCE_DATA"]
    return LazyArray(hdu.data, header=dict(hdu.header), hdu=hdulist)


@pytest.fixture
def lazy_array_from_numpy(small_numpy_array):
    """LazyArray wrapping a small in-memory numpy array — fast, no I/O."""
    from mertisreader.lazy_loading import LazyArray

    return LazyArray(small_numpy_array.copy(), header={"TEST": True})


@pytest.fixture
def lazy_array_with_nan(small_numpy_array_with_nan):
    """LazyArray wrapping an array that contains NaN/Inf values."""
    from mertisreader.lazy_loading import LazyArray

    return LazyArray(small_numpy_array_with_nan.copy(), header={})


# ---------------------------------------------------------------------------
# LazyCSVLoader fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def lazy_csv_from_real_file(raw_hk_csv, raw_hk_xml):
    """LazyCSVLoader backed by a real HK DAT file with column names from LBLX."""
    from mertisreader.lazy_loading import LazyCSVLoader
    from mertisreader.core import extract_mertis_hk_columns

    columns = extract_mertis_hk_columns(raw_hk_csv)
    return LazyCSVLoader(raw_hk_csv, columns=columns)


@pytest.fixture
def tmp_csv_file(tmp_path):
    """Minimal headerless CSV data (like real HK DAT files)."""
    csv_path = tmp_path / "test_data.csv"
    csv_path.write_text("1,2,3\n4,5,6\n7,8,9\n")
    return csv_path


@pytest.fixture
def tmp_empty_csv(tmp_path):
    """Truly empty file — no header, no data rows."""
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("")
    return csv_path


@pytest.fixture
def tmp_corrupted_csv(tmp_path):
    """Binary garbage file that cannot be parsed as CSV."""
    bad = tmp_path / "corrupted.csv"
    bad.write_bytes(b"\x00\x01\x02\x03\xFF\xFE\xFD")
    return bad


# ---------------------------------------------------------------------------
# Synthetic FITS fixtures for error-path tests
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_valid_fits(tmp_path):
    """Minimal valid FITS file with a small science array."""
    fits_path = tmp_path / "valid.fits"
    data = np.ones((4, 5, 6), dtype=np.float32)
    hdu = fits.PrimaryHDU(data)
    hdulist = fits.HDUList([hdu])
    hdulist.writeto(str(fits_path))
    return fits_path


@pytest.fixture
def tmp_corrupted_fits(tmp_path):
    """Binary garbage file that cannot be opened as FITS."""
    bad = tmp_path / "corrupted.fits"
    bad.write_bytes(b"\x00\x01\x02\x03\xFF\xFE\xFD")
    return bad


# ---------------------------------------------------------------------------
# MERTISDataPackReader fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def reader_raw(raw_dir):
    """MERTISDataPackReader initialised on the RAW sub-directory."""
    from mertisreader.core import MERTISDataPackReader

    return MERTISDataPackReader(raw_dir)


@pytest.fixture(scope="session")
def reader_cal(cal_dir):
    """MERTISDataPackReader initialised on the CAL sub-directory."""
    from mertisreader.core import MERTISDataPackReader

    return MERTISDataPackReader(cal_dir)


@pytest.fixture(scope="session")
def reader_par(par_dir):
    """MERTISDataPackReader initialised on the PAR sub-directory."""
    from mertisreader.core import MERTISDataPackReader

    return MERTISDataPackReader(par_dir)
