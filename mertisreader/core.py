__all__ = ['MERTISDataPackReader']

import pathlib
import re
import rich
import numpy as np
import pandas as pd
import logging
from typing import Union
import matplotlib.pyplot as plt

# Import extract_mertis_hk_columns from pds4_validation module (ADR-008)
from .pds4_validation import extract_mertis_hk_columns

# Import normalize_raw_axis_order from frame_utils module (for RAW level axis normalization)
from .frame_utils import normalize_raw_axis_order


class MERTISDataPackReader:
    """
    Class to read and process MERTIS data.

    Attributes:
        input_dir (pathlib.Path): Input directory.
        output_dir (pathlib.Path): Output directory.
        log_level (str): Log level.
        fits_files (list): List of FITS files.
        input_path_dict (dict): Dictionary of input paths.
        collect_data (dict): Dictionary of collected data.
    """
    def __init__(self, input_dir, output_dir='', log_level='', lazy=False):
        """
        Initialize the MERTISDataPackReader.

        Args:
            input_dir (str or pathlib.Path): Input directory.
            output_dir (str or pathlib.Path, optional): Output directory. Defaults to ''.
            log_level (str, optional): Log level. Defaults to ''.
            lazy (bool, optional): Enable lazy loading mode. Defaults to False.
        """
        self.input_dir = pathlib.Path(input_dir)
        self.output_dir = self.set_output_dir(output_dir)
        self.log_level = log_level
        self.lazy = lazy
        self.log = self.set_logger()
        logging.info(f'{input_dir=}')
        self.fits_files = self.get_fits_files()
        self.input_path_dict = self.get_input_path_dict()
        self.processing_level = self.detect_processing_level()
        self._frames_cache = None


    def detect_processing_level(self):
        """
        Detects the processing level (RAW, CAL, PAR) from the files in the input directory.
        Ensures all files have the same level.
        """
        levels = set()
        for f in self.fits_files:
            fname = f.name.lower()
            if fname.startswith("mer_raw_"):
                levels.add("RAW")
            elif fname.startswith("mer_cal_"):
                levels.add("CAL")
            elif fname.startswith("mer_par_"):
                levels.add("PAR")
        if len(levels) == 0:
            return "UNKNOWN"
        if len(levels) > 1:
            raise ValueError(f"Multiple processing levels found in input_dir: {levels}")
        return levels.pop()

    def __str__(self):
        info = [
            f"MERTISDataPackReader(",
            f"  input_dir={self.input_dir}",
            f"  output_dir={self.output_dir}",
            f"  log_level={self.log_level}",
        ]
        if hasattr(self, "input_path_dict"):
            info.append("  file counts: {")
            for k, v in self.input_path_dict.items():
                info.append(f"    {k}: {len(v)}")
            info.append("  }")
        info.append(")")
        return "\n".join(info)

    def __repr__(self):
        return (f"<MERTISDataPackReader(input_dir={self.input_dir!r}, "
                f"output_dir={self.output_dir!r}, "
                f"log_level={self.log_level!r})>")

    def set_output_dir(self, output_dir):
        """
        Set the output directory.

        Args:
            output_dir (str or pathlib.Path): Output directory.

        Returns:
            pathlib.Path: Output directory.
        """
        if output_dir:
            return pathlib.Path(output_dir)
        else:
            return self.input_dir.parent / f'{self.input_dir.name}-analysis_products'

    def set_logger(self):
        """
        Set the logger.
        """
        log_level = 'WARNING' if not self.log_level else self.log_level
        logging.basicConfig(format='%(asctime)s|%(process)d|%(levelname)s|%(message)s',
                            level=logging.getLevelName(log_level))
        logger = logging.getLogger()
        return logger

    def get_fits_files(self):
        """
        Get the list of FITS files.

        Returns:
            list: List of FITS files.
        """
        return list(self.input_dir.glob('**/*tis*.fits')) + \
               [i for i in self.input_dir.glob('**/*_hk_*.dat') if 'tis' not in i.stem and 'tir' not in i.stem]

    def get_input_path_dict(self):
        """
        Get the dictionary of input paths.

        Returns:
            dict: Dictionary of input paths.
        """
        files_type = ['hk_default', 'hk_extended', 'sc_tis', 'sc_tir', 'sc_tis_ql', 'sc_tir_ql']
        return {
            ft: list(
                sorted(
                    filter(lambda x: ft in str(x.stem), self.fits_files),
                    key=lambda x: int(x.stem.split('_')[-1])
                )
            )
            for ft in files_type
        }

    def show_files(self):
        """
        Print statistics about the files in the input directory.

        Prints the number of files in the input directory and the number of files
        in the input directory that match the old pattern '\\d{8}_\\d{8}' and the new pattern
        'mer_cal_sc_tis_YYYYMMDD_\\d+-\\d+-\\d+__\\d+_\\d+.fits'.
        """
        from collections import Counter
        # Old pattern: 8 digits underscore 8 digits
        regex_old = re.compile(r'\d{8}_\d{8}')
        # New pattern: mer_cal_sc_tis_YYYYMMDD_1-0651130819-21186__0_1.fits
        regex_new = re.compile(r'mer_cal_sc_tis_\d{8}_\d+-\d+-\d+__\d+_\d+\.fits')

        print('All files in input_dir :')
        rich.print(Counter([p.suffix for p in self.input_dir.rglob('*')]))

        print('All files in input_dir matching old pattern <v0.2.6 (\\d{8}_\\d{8}):')
        rich.print(Counter([re.findall('^([^\\d]*)_', p.stem)[0] for p in self.input_dir.rglob('*') if regex_old.search(p.stem)]))

        print('All files in input_dir matching new pattern >=v0.2.6 (mer_cal_sc_tis_YYYYMMDD_1-...):')
        rich.print(Counter([re.findall('^(mer_cal_sc_tis)', p.name)[0] for p in self.input_dir.rglob('*') if regex_new.match(p.name)]))

    def filetypes2dict(self):
        """
        Convert the input files into a dictionary, where the keys are the file types and the values are lists of file paths.

        Returns:
            dict: A dictionary where the keys are the file types and the values are lists of file paths.
        """
        # Define the file types.
        files_type = ['hk_default', 'hk_extended', 'sc_tis', 'sc_tir', 'sc_tis_ql', 'sc_tir_ql']

        # Create a dictionary to store the file paths.
        input_path_dict = {}

        # Iterate over each file type.
        for ft in files_type:
            # Filter the fits files based on the file type.
            # Sort the filtered files based on the numeric part in the file name.
            # Convert the result to a list.
            input_path_dict[ft] = list(
                sorted(
                    filter(lambda x: ft in str(x.stem), self.fits_files),
                    key=lambda x: int(x.stem.split('_')[-1])
                )
            )

        # Return the dictionary.
        return input_path_dict

    def listfiletypes(self) :
        """
        Print the list of file types and the number of files for each file type.

        This function iterates over the input_path_dict dictionary and prints the file types and the number
        of files for each file type. The file types and the number of files are printed using the rich.print
        function.

        Returns:
            None
        """
        # Iterate over the input_path_dict dictionary and print the file types and the number of files for each file type.
        rich.print({k: [f.name for f in v] for k, v in self.input_path_dict.items()})

        # Print the number of files for each file type.
        rich.print({filetype:len(files_paths) for filetype,files_paths in self.input_path_dict.items()})

    def save_plot(self,
                  out_file,
                  dpi=150,
                  out_format='jpg'):
        """
        Save a plot to the output directory.

        Args:
            out_file (str): The name of the output file.
            dpi (int): The resolution of the saved image in dots per inch. Default is 150.
            out_format (str): The format of the saved image. Default is 'jpg'.

        Returns:
            None
        """
        # Construct the output file path by joining the output directory and the output file name.
        out_path = self.output_dir / (out_file +f'.{out_format}' )

        # Save the plot to the output file path with the specified resolution and format.
        plt.savefig(out_path,dpi=dpi)

        # Print a message indicating that the plot is being saved.
        print(f'Saving {out_path}')

    def _get_tis_science_hdu_names(self):
        """Return candidate TIS science HDU names for the detected processing level."""
        level = self.processing_level
        if level == "RAW":
            return ["MERTIS_TIS_RAW_SCIENCE_DATA"]
        if level == "CAL":
            return ["MERTIS_TIS_CAL_SCIENCE_DATA", "MERTIS_TIS_CALIB_SCIENCE_DATA"]
        if level == "PAR":
            return ["MERTIS_TIS_PAR_SCIENCE_DATA"]
        return [
            "MERTIS_TIS_RAW_SCIENCE_DATA",
            "MERTIS_TIS_CAL_SCIENCE_DATA",
            "MERTIS_TIS_CALIB_SCIENCE_DATA",
            "MERTIS_TIS_PAR_SCIENCE_DATA",
        ]

    def data_collector(self):
        """
        Collect data from the input files and store it in the collect_data attribute.

        This function iterates over the input_path_dict dictionary, which contains the file paths for each file type.
        For each file type, it checks if there are files available and reads the data from the files.
        The collected data is stored in the collect_data attribute.

        In lazy mode (self.lazy=True), FITS data is wrapped in LazyArray and HK data in LazyCSVLoader
        to defer I/O until data is actually accessed.

        Returns:
            None
        """
        from astropy.io import fits

        # Import lazy loading classes
        from mertisreader.lazy_loading import LazyArray, LazyCSVLoader

        # Create an empty dictionary to store the collected data
        collect_data = {}

        # Iterate over the input_path_dict dictionary
        for filetype, files_paths in self.input_path_dict.items():

            # Check if the file type contains 'hk'
            if 'hk' in filetype:
                # Skip if there are no files
                if len(files_paths) == 0:
                    continue

                # Iterate over the files for the current file type
                for in_file in files_paths:
                    print(f'Reading filetype: {filetype} from {in_file.stem}')

                    # Add the data to the collect_data dictionary
                    if filetype not in collect_data:
                        collect_data[filetype] = []

                    if self.lazy:
                        # Lazy mode: wrap in LazyCSVLoader
                        collect_data[filetype].append({
                            'data': LazyCSVLoader(in_file, columns=extract_mertis_hk_columns(in_file)),
                            'path': in_file
                        })
                    else:
                        # Eager mode: load immediately
                        data = pd.read_csv(in_file, names=extract_mertis_hk_columns(in_file))
                        collect_data[filetype].append({
                            'data': data,
                            'path': in_file
                        })

            # Check if the file type contains 'sc_tis' or 'sc_tir'
            elif ('sc_tis' in filetype) or ('sc_tir' in filetype):
                # Remove the 'sc_' prefix from the file type
                filetype = re.sub('^sc_', '', filetype)

                # Skip if there are no files
                if len(files_paths) == 0:
                    continue

                # Iterate over the files for the current file type
                for in_file in files_paths:
                    print(f'Reading filetype: {filetype} from {in_file.stem}')

                    # Add the data to the collect_data dictionary
                    if filetype not in collect_data:
                        collect_data[filetype] = []

                    if self.lazy:
                        # Lazy mode: open with memmap and wrap in LazyArray
                        hdulist = fits.open(str(in_file), memmap=True, do_not_scale_image_data=True)
                        science_data = None
                        for hdu_name in self._get_tis_science_hdu_names():
                            if hdu_name in hdulist:
                                science_data = hdulist[hdu_name]
                                break
                        if science_data is None:
                            raise KeyError(
                                f"No matching science HDU found for processing level {self.processing_level!r} in {in_file}"
                            )
                        lazy_array = LazyArray(science_data.data, header=dict(science_data.header), hdu=science_data)
                        collect_data[filetype].append({
                            'fits_data': lazy_array,
                            'path': in_file
                        })
                    else:
                        # Eager mode: load immediately
                        hdulist = fits.open(str(in_file))
                        collect_data[filetype].append({
                            'fits_data': hdulist,
                            'path': in_file
                        })

        # Store the collected data in the collect_data attribute
        self.collect_data = collect_data


    def data_assembler(self, verbose=False):
        """
        Assembles the collected data into convenient data structures.

        This function processes the collected data and stores it in convenient data structures. The processed data includes:
        - ``geom_ls``: a dictionary of dictionaries, where each dictionary contains the data for a specific file, and each inner dictionary contains the data for a specific parameter.
        - ``frames``: a dictionary of numpy arrays, where each array contains the data for a specific file.
        - ``wavelengths``: a dictionary of numpy arrays, where each array contains the wavelength data for a specific file.
        - ``mertis_tis_metadata``: a dictionary of pandas DataFrames, where each DataFrame contains the metadata for a specific file.
        - ``space_index``: a pandas Index object containing the indices of the space measurements.
        - ``bb7_index``: a pandas Index object containing the indices of the BB7 measurements.
        - ``bb3_index``: a pandas Index object containing the indices of the BB3 measurements.
        - ``planet_index``: a pandas Index object containing the indices of the planet measurements.
        """
        from astropy.table import Table, vstack
        from astropy.time import Time
        from rich.progress import track

        # call data_collector if no data loaded
        if not hasattr(self, 'collect_data'):
            self.data_collector()

        NODATA_GEOMETRY = -1.7976931348623157e+308 # min double, this is new

        # Initialize the data structures
        geom_ls = {}
        frames = {}
        wavelengths = {}
        mertis_tis_metadata = {}
        output_str = []

        # Iterate over the collected tis data
        for tis_data in track(self.collect_data["tis"],
                              total=len(self.collect_data["tis"]),
                              description="Loading files..."):
            if "table" not in tis_data["path"].name:
                tis_data_path_stem = tis_data["path"].stem
                # Read the data from the FITS file and convert it to a pandas DataFrame
                tmp_table = Table(tis_data["fits_data"][1].data).to_pandas()
                mertis_tis_metadata[tis_data_path_stem] = tmp_table

                print(f'Reading filetype: tis from {tis_data["path"]}')
                # Convert the data to float64 to keep the native byteorder
                # new version >=0.2.6
                level = self.processing_level
                if level == "PAR":
                    frames[tis_data_path_stem] = tis_data["fits_data"]['MERTIS_TIS_PAR_SCIENCE_DATA'].data.astype(np.float64)
                    wavelengths[tis_data_path_stem] = tis_data["fits_data"]['MERTIS_TIS_PAR_SCIENCE_DATA_WAVELENGTH'].data.astype(np.float64)
                elif level == "RAW":
                    frames[tis_data_path_stem] = tis_data["fits_data"]['MERTIS_TIS_RAW_SCIENCE_DATA'].data.astype(np.float64)
                    # Normalize RAW axis order from (temp, pix, spec) to (spec, pix, temp)
                    frames[tis_data_path_stem] = normalize_raw_axis_order(frames[tis_data_path_stem])
                    wavelengths[tis_data_path_stem] = None  # or np.nan, or skip, as appropriate
                elif level == "CAL":
                    try:
                        frames[tis_data_path_stem] = tis_data["fits_data"]['MERTIS_TIS_CAL_SCIENCE_DATA'].data.astype(np.float64)
                        wavelengths[tis_data_path_stem] = tis_data["fits_data"]['MERTIS_TIS_CAL_SCIENCE_DATA_WAVELENGTH'].data.astype(np.float64)
                    except KeyError:
                        frames[tis_data_path_stem] = tis_data["fits_data"]['MERTIS_TIS_CALIB_SCIENCE_DATA'].data.astype(np.float64)
                        wavelengths[tis_data_path_stem] = tis_data["fits_data"]['MERTIS_TIS_CALIB_SCIENCE_DATA_WAVELENGTH'].data.astype(np.float64)
                else:
                    raise ValueError(f"Unknown TIS file level for {level}")

                # Only process geometry if not RAW
                if level != "RAW":
                    geom_ls[tis_data_path_stem] = {k.name: k.data.astype(np.float64) for k in tis_data["fits_data"] if 'GEOM' in k.name}
                    for geo_k, geo_v in geom_ls[tis_data["path"].stem].items():
                        geo_v[geo_v == NODATA_GEOMETRY] = np.nan
                    geo_k = 'MERTIS_TIS_GEOMETRY_TARGET_LONGITUDE'
                    output_str.append([tis_data_path_stem, np.sum(np.isfinite(geo_v)), geo_v.size])

        # Preserve the original index in the source file
        mertis_tis_metadata_df = pd.concat(mertis_tis_metadata).reset_index(drop=False).drop(columns=['level_0']).rename(columns={"level_1": "file_index"})

        # Sort the metadata DataFrame by the TIME_UTC column
        mertis_tis_metadata_df_time_utc_sort_index = mertis_tis_metadata_df.sort_values('TIME_UTC').index.values
        mertis_tis_metadata_df = mertis_tis_metadata_df.sort_values('TIME_UTC').reset_index(drop=True)
        mertis_tis_metadata_df['TIME_UTC'] = pd.to_datetime(mertis_tis_metadata_df['TIME_UTC'], utc=True)

        # Identify the indices of the space, BB7, BB3, and planet measurements in the merged metadata DataFrame for all files
        space_index_merged = mertis_tis_metadata_df[mertis_tis_metadata_df['HK_STAT_TIS_DATA_ACQ_TARGET'].str.contains('Space')].index
        bb7_index_merged = mertis_tis_metadata_df[mertis_tis_metadata_df['HK_STAT_TIS_DATA_ACQ_TARGET'].str.contains('BB7')].index
        bb3_index_merged = mertis_tis_metadata_df[mertis_tis_metadata_df['HK_STAT_TIS_DATA_ACQ_TARGET'].str.contains('BB3')].index
        planet_index_merged = mertis_tis_metadata_df[mertis_tis_metadata_df['HK_STAT_TIS_DATA_ACQ_TARGET'].str.contains('Planet')].index

        # Map the merged indices back to the original file-specific indices
        space_index = {k:v[v['HK_STAT_TIS_DATA_ACQ_TARGET'].str.contains('Space')].index for k,v in mertis_tis_metadata.items()}
        bb7_index = {k:v[v['HK_STAT_TIS_DATA_ACQ_TARGET'].str.contains('BB7')].index for k,v in mertis_tis_metadata.items()}
        bb3_index = {k:v[v['HK_STAT_TIS_DATA_ACQ_TARGET'].str.contains('BB3')].index for k,v in mertis_tis_metadata.items()}
        planet_index = {k:v[v['HK_STAT_TIS_DATA_ACQ_TARGET'].str.contains('Planet')].index for k,v in mertis_tis_metadata.items()}


        if level != "RAW":
            ########################################################################
            # generic wavelengths : not precise enough for scientific analysis!
            wav = wavelengths[list(wavelengths.keys())[-1]].mean(axis=1)
            n_wav = len(wav)
            n_corners = geom_ls[list(geom_ls.keys())[0]]['MERTIS_TIS_GEOMETRY_TARGET_LONGITUDE'].shape[0]

        # Print the output statistics
        if verbose:
            if level != "RAW":
                print(f'{n_wav=} # generic wavelengths : not precise enough for scientific analysis!')
                print(pd.DataFrame(columns=["tis_stem", "finite(geo)", "geo.size"], data=output_str).to_markdown())
            print("Indices of measurements targets (HK_STAT_TIS_DATA_ACQ_TARGET):")
            print(f'{space_index_merged.shape=}')
            print(f'{bb7_index_merged.shape=}')
            print(f'{bb3_index_merged.shape=}')
            print(f'{planet_index_merged.shape=}')
            # Print the collected data statistics
            print(f'Collected data statistics:')
            print(f'Number of TIS files: {len(self.collect_data.get("tis", []))}')
            print(f'Number of HK files: {len(self.collect_data.get("hk_default", [])) + len(self.collect_data.get("hk_extended", []))}')
            print(f'Number of TIR files: {len(self.collect_data.get("tir", []))}')
            print(f'Number of TIS QL files: {len(self.collect_data.get("tis_ql", []))}')
            print(f'Number of TIR QL files: {len(self.collect_data.get("tir_ql", []))}')
        # Store the processed data in the corresponding attributes
        self.geom_ls = geom_ls
        self.frames = frames
        self.wavelengths = wavelengths
        self.mertis_tis_metadata = mertis_tis_metadata
        self.space_index = space_index
        self.bb7_index = bb7_index
        self.bb3_index = bb3_index
        self.planet_index = planet_index
        self.space_index_merged = space_index_merged
        self.bb7_index_merged = bb7_index_merged
        self.bb3_index_merged = bb3_index_merged
        self.planet_index_merged = planet_index_merged

    def get_original_frames(self):
        """
        Return the original frames dictionary after assembly.

        Per ADR-004: This method is cached - returns the same object on subsequent calls.

        Returns:
            dict: The frames dictionary with keys as file stems and values as 3D numpy arrays.

        Raises:
            RuntimeError: If data_assembler() has not been called yet.
        """
        if not hasattr(self, 'frames'):
            raise RuntimeError(
                "data_assembler() must be called before get_original_frames(). "
                "Call reader.data_assembler() first."
            )
        # Cache the frames dict for subsequent calls
        if self._frames_cache is None:
            self._frames_cache = self.frames
        return self._frames_cache

    def get_tis_product(self, file_key=None):
        """
        Get a TIS product with lazy-loaded science data and metadata.

        Convenience helper for accessing TIS data without manually navigating
        collect_data and re-opening FITS files. Per ADR-006, returns LazyArray
        wrappers that defer I/O until data is accessed.

        Args:
            file_key (str, optional): File stem/key to retrieve. If None, returns
                the first available TIS file.

        Returns:
            dict: Dictionary with keys:
                - 'fits': astropy.io.fits.HDUList (memmap)
                - 'frames': LazyArray for science data
                - 'wavelengths': LazyArray or None
                - 'metadata': LazyCSVLoader or None (for HK files)
                - 'path': pathlib.Path to the FITS file

        Raises:
            RuntimeError: If data_collector() has not been called.
            ValueError: If no TIS files are available or file_key not found.

        Example:
            >>> reader = MERTISDataPackReader(dir, lazy=True)
            >>> reader.data_collector()
            >>> product = reader.get_tis_product()  # first file
            >>> frames = product['frames']  # LazyArray, no I/O yet
            >>> print(frames.shape)  # Still no I/O
            >>> data = frames.materialize()  # Now I/O happens
        """
        if not hasattr(self, 'collect_data'):
            raise RuntimeError(
                "data_collector() must be called before get_tis_product(). "
                "Call reader.data_collector() first."
            )

        tis_entries = self.collect_data.get('tis', [])
        if not tis_entries:
            raise ValueError(f"No TIS files available in {self.input_dir}")

        # Select file
        if file_key is None:
            entry = tis_entries[0]
        else:
            matching = [e for e in tis_entries if e['path'].stem == file_key]
            if not matching:
                raise ValueError(f"No TIS file found with key {file_key!r}")
            entry = matching[0]

        fits_path = entry['path']
        lazy_frames = entry['fits_data']  # Already a LazyArray

        # Open FITS file for header/metadata access (memmap, no scaling)
        from astropy.io import fits
        hdulist = fits.open(str(fits_path), memmap=True, do_not_scale_image_data=True)

        # Find wavelength HDU
        wavelengths = None
        level = self.processing_level
        science_hdu_name = None

        for hdu_name in self._get_tis_science_hdu_names():
            if hdu_name in hdulist:
                science_hdu_name = hdu_name
                break

        # Look for corresponding wavelength HDU
        if science_hdu_name:
            wav_hdu_name = science_hdu_name.replace('_SCIENCE_DATA', '_SCIENCE_DATA_WAVELENGTH')
            if wav_hdu_name in hdulist:
                from .lazy_loading import LazyArray
                wav_data = hdulist[wav_hdu_name].data
                lazy_wav = LazyArray(wav_data, header=dict(hdulist[wav_hdu_name].header))
                wavelengths = lazy_wav

        # Metadata from HK files if available
        metadata = None
        hk_entries = self.collect_data.get('hk_default', []) or self.collect_data.get('hk_extended', [])
        if hk_entries:
            # Just use the first HK entry - don't check columns (triggers schema resolution)
            metadata = hk_entries[0]['data']

        return {
            'fits': hdulist,
            'frames': lazy_frames,
            'wavelengths': wavelengths,
            'metadata': metadata,
            'path': fits_path
        }

    def get_frames(self, file_key=None):
        """
        Get science frames dictionary with lazy-loaded arrays.

        Args:
            file_key (str, optional): Specific file key. If None, returns all files.

        Returns:
            dict or LazyArray: If file_key provided, returns LazyArray for that file.
                Otherwise returns dict {file_key: LazyArray}.

        Raises:
            RuntimeError: If data_collector() has not been called.
        """
        if not hasattr(self, 'collect_data'):
            raise RuntimeError(
                "data_collector() must be called before get_frames(). "
                "Call reader.data_collector() first."
            )

        tis_entries = self.collect_data.get('tis', [])
        if not tis_entries:
            return {}

        if file_key is None:
            return {e['path'].stem: e['fits_data'] for e in tis_entries}
        else:
            for entry in tis_entries:
                if entry['path'].stem == file_key:
                    return entry['fits_data']
            raise ValueError(f"No TIS file found with key {file_key!r}")

    def get_wavelengths(self, file_key=None):
        """
        Get wavelength data for TIS products.

        Args:
            file_key (str, optional): Specific file key. If None, returns dict of all files.

        Returns:
            dict or LazyArray or None: Wavelength data as LazyArray (lazy-loaded).
                Returns None if wavelengths not available (e.g., RAW level).

        Raises:
            RuntimeError: If data_collector() has not been called.
        """
        if not hasattr(self, 'collect_data'):
            raise RuntimeError(
                "data_collector() must be called before get_wavelengths(). "
                "Call reader.data_collector() first."
            )

        from astropy.io import fits
        from .lazy_loading import LazyArray

        tis_entries = self.collect_data.get('tis', [])
        if not tis_entries:
            return {} if file_key is None else None

        result = {}
        for entry in tis_entries:
            fits_path = entry['path']
            hdulist = fits.open(str(fits_path), memmap=True, do_not_scale_image_data=True)

            # Find wavelength HDU
            wav_hdu_name = None
            for hdu_name in self._get_tis_science_hdu_names():
                if hdu_name in hdulist:
                    wav_hdu_name = hdu_name.replace('_SCIENCE_DATA', '_SCIENCE_DATA_WAVELENGTH')
                    break

            if wav_hdu_name and wav_hdu_name in hdulist:
                wav_data = hdulist[wav_hdu_name].data
                result[entry['path'].stem] = LazyArray(wav_data, header=dict(hdulist[wav_hdu_name].header))

        if file_key is None:
            return result
        else:
            return result.get(file_key)

    def get_metadata(self, file_type='hk_default', file_key=None):
        """
        Get metadata (HK data) from collected files.

        Args:
            file_type (str): Type of HK data ('hk_default' or 'hk_extended').
            file_key (str, optional): Specific file key. If None, returns dict of all files.

        Returns:
            dict or LazyCSVLoader or pd.DataFrame: Metadata as LazyCSVLoader in lazy mode,
                or DataFrame in eager mode.
        """
        if not hasattr(self, 'collect_data'):
            raise RuntimeError(
                "data_collector() must be called before get_metadata(). "
                "Call reader.data_collector() first."
            )

        entries = self.collect_data.get(file_type, [])
        if not entries:
            return {} if file_key is None else None

        if file_key is None:
            return {e['path'].stem: e['data'] for e in entries}
        else:
            for entry in entries:
                if entry['path'].stem == file_key:
                    return entry['data']
            # Try without file_key filter
            return {e['path'].stem: e['data'] for e in entries}
