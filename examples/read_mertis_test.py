# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: mertis
#     language: python
#     name: python3
# ---

# %% [markdown]
# # MERTIS reader walkthrough
#
# This example shows the current public API in a way that is useful for users:
#
# - discover a sample data pack
# - load it with `MERTISDataPackReader`
# - inspect the assembled science products
# - preview lazy loading
# - validate a PDS4 label when `pds4_tools` is available

# %%
from pathlib import Path
from pprint import pprint
from typing import Optional

import matplotlib.pyplot as plt
import rich

import mertisreader as mr

print("Libraries imported successfully.")


# %%
def find_repo_root(start: Optional[Path] = None) -> Path:
    """Find the repository root by looking for the data and package directories."""
    import mertisreader as _mr  # noqa: E402 – local import to avoid circular deps

    anchor = Path(start or Path.cwd()).resolve()
    if not ((anchor / "data").exists() and (anchor / "mertisreader").exists()):
        file_anchor = Path(_mr.__file__).resolve().parent.parent
        if (file_anchor / "data").exists() and (file_anchor / "mertisreader").exists():
            anchor = file_anchor

    for candidate in (anchor, *anchor.parents):
        if (candidate / "data").exists() and (candidate / "mertisreader").exists():
            return candidate
    raise FileNotFoundError("Could not locate the repository root.")


def find_label_path(data_path: Path) -> Optional[Path]:
    """Return the first matching PDS4 label path next to a data file."""
    for suffix in (".lblx", ".xml", ".lbl"):
        candidate = data_path.with_suffix(suffix)
        if candidate.exists():
            return candidate
    return None


def summarize_reader(reader: mr.MERTISDataPackReader) -> None:
    """Print a compact summary of the reader state."""
    print(f"Processing level: {reader.processing_level}")
    print(f"Lazy mode: {reader.lazy}")
    print(f"Input directory: {reader.input_dir}")
    print(f"Output directory: {reader.output_dir}")
    print("File counts:")
    rich.print({name: len(paths) for name, paths in reader.input_path_dict.items()})


# %%
repo_root = find_repo_root()
pack_root = repo_root / "data" / (
    "bcmer_tm_all_START-20200409T000000_END-20200410T000000"
    "_CRE-20240717T132010-ParamEventBootSciHK-short"
)
cal_dir = pack_root / "cal"
raw_dir = pack_root / "raw"
output_path = Path("/tmp")

if not cal_dir.exists():
    raise FileNotFoundError(f"Sample CAL directory not found: {cal_dir}")

print(f"Repository root: {repo_root}")
print(f"Sample CAL directory: {cal_dir}")
print(f"Sample RAW directory: {raw_dir}")


# %%
reader = mr.MERTISDataPackReader(
    input_dir=cal_dir,
    output_dir=str(output_path),
    log_level="INFO",
)
summarize_reader(reader)


# %%
reader.show_files()
reader.listfiletypes()


# %%
reader.data_collector()
print(f"Collected groups: {sorted(reader.collect_data.keys())}")
for key, value in reader.collect_data.items():
    print(f"{key}: {len(value)} files")


# %%
reader.data_assembler(verbose=True)
print("Assembled frames:")
rich.print({key: value.shape for key, value in reader.frames.items()})

first_key = next(iter(reader.frames))
print(f"Example frame key: {first_key}")
print(f"Example frame shape: {reader.frames[first_key].shape}")
print(reader.mertis_tis_metadata[first_key].head())


# %%
if reader.processing_level != "RAW":
    print(f"Geometry keys: {list(reader.geom_ls[first_key].keys())[:5]}")
    print(f"Space index merged shape: {reader.space_index_merged.shape}")
    print(f"BB7 index merged shape: {reader.bb7_index_merged.shape}")
    print(f"BB3 index merged shape: {reader.bb3_index_merged.shape}")
    print(f"Planet index merged shape: {reader.planet_index_merged.shape}")


# %%
if reader.processing_level != "RAW" and reader.wavelengths[first_key] is not None:
    full_frames_3d = reader.frames[first_key]
    wav = reader.wavelengths[first_key]
    plot_index = reader.space_index[first_key]

    fig, ax = plt.subplots(ncols=2, nrows=2, figsize=(18, 10))
    fig.suptitle(
        f"MERTIS TIS DataCube - {first_key}\n"
        f"average over the measurements {full_frames_3d.shape} -> {full_frames_3d[:, :, 0].shape}",
        fontsize=14,
    )

    title = "Space"
    mean_image = full_frames_3d[:, :, plot_index].mean(axis=2)
    std_image = full_frames_3d[:, :, plot_index].std(axis=2)

    ax[0][0].plot(wav, mean_image.mean(axis=1))
    ax[0][0].set_title(f"{title} - frames average")
    ax[0][1].imshow(mean_image, aspect="auto", cmap=plt.cm.Spectral_r)
    ax[0][1].set_title(f"{title} - frames average")

    ax[1][0].plot(wav, std_image.mean(axis=1))
    ax[1][0].set_title(f"{title} - frames std")
    ax[1][1].imshow(std_image, aspect="auto", cmap=plt.cm.Spectral_r)
    ax[1][1].set_title(f"{title} - frames std")

    for axis in ax[:, 0]:
        axis.set_xlabel("Wavelength [nm]")
        axis.set_ylabel("Radiance [W/m2/sr/nm]")
        axis.grid(True)

    for axis in ax[:, 1]:
        axis.set_xlabel("Frame Index")
        axis.set_ylabel("Wavelength Index")

    plt.tight_layout()


# %%
lazy_reader = mr.MERTISDataPackReader(
    input_dir=cal_dir,
    output_dir=str(output_path),
    log_level="INFO",
    lazy=True,
)
lazy_reader.data_collector()

print(f"Lazy reader collected groups: {sorted(lazy_reader.collect_data.keys())}")

lazy_tis = lazy_reader.collect_data.get("tis", [])
if lazy_tis:
    sample_lazy_tis = lazy_tis[0]["fits_data"]
    print(f"Lazy TIS proxy type: {type(sample_lazy_tis).__name__}")
    print(sample_lazy_tis)

lazy_hk = lazy_reader.collect_data.get("hk_default", [])
if lazy_hk:
    sample_lazy_hk = lazy_hk[0]["data"]
    print(f"Lazy HK proxy type: {type(sample_lazy_hk).__name__}")
    print(sample_lazy_hk)
    print("Lazy HK preview:")
    try:
        pprint(sample_lazy_hk.materialize().head())
    except Exception as exc:
        print(f"Could not materialize lazy HK data: {exc}")


# %%
sample_hk_files = sorted(raw_dir.glob("mer_raw_hk_default_*.dat")) if raw_dir.exists() else []
if sample_hk_files:
    sample_hk = sample_hk_files[0]
    label_path = find_label_path(sample_hk)

    print(f"Sample HK file: {sample_hk.name}")
    print("Extracted HK columns:")
    rich.print(mr.extract_mertis_hk_columns(sample_hk)[:10])

    if label_path is None:
        print("No matching label file found next to the sample HK file.")
    elif mr.PDS4_TOOLS_AVAILABLE:
        print(f"Label file: {label_path.name}")

        validation = mr.validate_pds4_label(label_path)
        print(f"PDS4 label valid: {validation['valid']}")
        if validation["warnings"]:
            print("Warnings:")
            rich.print(validation["warnings"])

        metadata = mr.extract_label_metadata(label_path)
        print("Label metadata:")
        pprint(metadata)

        try:
            field_metadata = mr.get_csv_field_metadata(sample_hk)
            print("Field metadata preview:")
            print(field_metadata.head())
        except Exception as exc:
            print(f"Could not extract field metadata: {exc}")
    else:
        print("pds4_tools is not installed, so label validation is skipped.")
else:
    print("No sample HK files were found in the RAW directory.")

# %%
