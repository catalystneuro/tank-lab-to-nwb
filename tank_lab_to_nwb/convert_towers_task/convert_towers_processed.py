"""Authors: Alessio Buccino, Cody Baker, Szonja Weigl, and Ben Dichter."""
from pathlib import Path
from isodate import duration_isoformat
from datetime import timedelta

from tank_lab_to_nwb import TowersProcessedNWBConverter

# Point to the base folder path for both recording data and Virmen
base_path = Path("D:/Neuropixels/")

# Name the NWBFile and point to the desired save path
nwbfile_path = base_path / "TowersProcessing_stub.nwb"

# Point to the various files for the conversion
recording_folder = base_path / "Neuropixels" / "A256_bank1_2020_09_30" / "A256_bank1_2020_09_30_g0"
raw_data_file = recording_folder / "A256_bank1_2020_09_30_g0_t0.imec0.ap.bin"
spikeinterface_folder = recording_folder / "spikeinterface"
recording_pickle_file = spikeinterface_folder / "raw.pkl"
sorting_pickle_file = spikeinterface_folder / "sorter1.pkl"
virmen_file_path = base_path / "TowersTask" / "PoissonBlocksReboot_cohort1_VRTrain6_E75_T_20181105.mat"

# Enter Session and Subject information here
# Comment out or remove any fields you do not want to include
session_description = "Enter session description here."

subject_info = dict(
    description="Enter optional subject description here",
    weight="Enter subject weight here",
    age=duration_isoformat(timedelta(days=0)),  # Enter the age of the subject in days
    species="Mus musculus",
    genotype="Enter subject genotype here",
    sex="Enter subject sex here"
)

# Set some global options
# Recommended to set stub_test to True for first conversion to allow fast testing/validation
stub_test = True



# Run the conversion
source_data = dict(
    SIRecording=dict(pkl_file=str(recording_pickle_file.absolute())),
    SISorting=dict(pkl_file=str(sorting_pickle_file.absolute())),
    VirmenData=dict(file_path=str(virmen_file_path.absolute()))
)
conversion_options = dict(
    SIRecording=dict(stub_test=stub_test),
    SISorting=dict(stub_test=stub_test)
)
converter = TowersProcessedNWBConverter(source_data)
metadata = converter.get_metadata()
metadata['NWBFile'].update(session_description=session_description)
metadata['Subject'].update(subject_info)
metadata.update(converter.get_spikeglx_metadata(raw_data_file))
converter.run_conversion(
    nwbfile_path=str(nwbfile_path.absolute()),
    metadata=metadata,
    conversion_options=conversion_options
)
