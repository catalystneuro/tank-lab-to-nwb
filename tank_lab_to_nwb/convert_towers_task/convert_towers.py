"""Authors: Cody Baker and Ben Dichter."""
from tank_lab_to_nwb import TankNWBConverter

# TODO: add pathlib
import os
from joblib import Parallel, delayed

n_jobs = 1  # number of parallel streams to run

base_path = "D:/Neuropixels/TowersTask"
# base_path = "/mnt/scrap/cbaker239/Neuropixels/TowersTask"

# Manual list of selected sessions that cause problems with the general functionality
exlude_sessions = []

experimenter = ""
paper_descr = ""
paper_info = ""

session_strings = ["PoissonBlocksReboot_cohort1_VRTrain6_E75_T_20181105"]
nwbfile_paths = []
for session in session_strings:
    nwbfile_paths.append(session + "_local_stub.nwb")


def run_tower_conv(session, nwbfile_path):
    """Conversion function to be run in parallel."""
    if os.path.exists(session):
        print(f"Processsing {session}...")
        if not os.path.isfile(nwbfile_path):
            # construct input_args dict according to input schema
            input_args = dict(
                source_data=dict(
                #     GLXRecording=dict(
                #         file_path="D:/Neuropixels/Neuropixels/A256_bank1_2020_09_30/"
                #         "A256_bank1_2020_09_30_g0/A256_bank1_2020_09_30_g0_t0.imec0.ap.bin"
                #     ),
                    TowerPosition=dict(folder_path=session)
                )
            )

            converter = TankNWBConverter(**input_args)
            metadata = converter.get_metadata()

            # Session specific info
            metadata['NWBFile'].update({'experimenter': experimenter})
            metadata['NWBFile'].update({'session_description': paper_descr})
            metadata['NWBFile'].update({'related_publications': paper_info})

            metadata['Subject'].update({'species': "Mus musculus"})

            # metadata[yuta_converter.get_recording_type()]['Ecephys']['Device'][0].update({'name': 'implant'})

            # for electrode_group_metadata in \
            #         metadata[yuta_converter.get_recording_type()]['Ecephys']['ElectrodeGroup']:
            #     electrode_group_metadata.update({'location': 'unknown'})
            #     electrode_group_metadata.update({'device_name': 'implant'})

            converter.run_conversion(nwbfile_path=nwbfile_path, metadata_dict=metadata,
                                     stub_test=True, save_to_file=True)
    else:
        print(f"The folder ({session}) does not exist!")


Parallel(n_jobs=n_jobs)(delayed(run_tower_conv)(session, nwbfile_path)
                        for session, nwbfile_path in zip(session_strings, nwbfile_paths)
                        if os.path.split(session)[1] not in exlude_sessions)
