"""Test the new lazy loading helper methods."""
import pathlib
import mertisreader as mr

# Test with a sample data path
base_data_path = pathlib.Path('~/Documents/programs_and_data/data/MERTIS/ESA').expanduser()
data_pack_path = base_data_path / 'OGS/flybys_mertis_flyby_5/bcmer_tm_all_20241201T000000_20241202T080000_20241201T200155-AccExecFailureParamEventBootSciHK'

if data_pack_path.exists():
    data_dir = data_pack_path / 'cal_cubic'
    output_path = pathlib.Path('/output')

    # Create reader with lazy loading
    ms_reader = mr.MERTISDataPackReader(
        input_dir=data_dir,
        output_dir=output_path,
        log_level='INFO',
        lazy=True
    )
    ms_reader.data_collector()

    print("\n=== Testing get_tis_product() ===")
    product = ms_reader.get_tis_product()
    print(f"Product keys: {product.keys()}")
    print(f"Frames (LazyArray): {product['frames']}")
    print(f"Frames shape (no I/O): {product['frames'].shape}")
    print(f"Wavelengths (LazyArray): {product['wavelengths']}")
    if product['wavelengths']:
        print(f"Wavelengths shape (no I/O): {product['wavelengths'].shape}")
    print(f"Path: {product['path'].name}")

    print("\n=== Testing get_frames() ===")
    frames_dict = ms_reader.get_frames()
    print(f"Frames dict keys: {list(frames_dict.keys())}")
    print(f"First frames: {list(frames_dict.values())[0]}")

    print("\n=== Testing get_wavelengths() ===")
    wav_dict = ms_reader.get_wavelengths()
    print(f"Wavelengths dict keys: {list(wav_dict.keys())}")
    if wav_dict:
        print(f"First wavelengths: {list(wav_dict.values())[0]}")

    print("\n=== All helpers working! ===")
else:
    print(f"Test data not found at {data_pack_path}")
    print("Skipping functional test - helpers implemented but not tested with real data")
