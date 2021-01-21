from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
from datetime import datetime

import spikeextractors as se
import spiketoolkit as st
import spikesorters as ss
import spikecomparison as sc
import spikewidgets as sw
from nwb_conversion_tools.conversion_tools import save_si_object

base_data_path = Path("D:/Neuropixels/ActualData/2021_01_15_E105/towersTask_g0/towersTask_g0_imec0")
ap_bin_path = base_data_path / "towersTask_g0_t0.imec0.ap.bin"
lf_bin_path = base_data_path / "towersTask_g0_t0.imec0.lf.bin"

recording_folder = ap_bin_path.parent
spikeinterface_folder = recording_folder / 'spikeinterface'
spikeinterface_folder.mkdir(parents=True, exist_ok=True)

stub_test = False
nsec_stub = 60*5

recording_ap = se.SpikeGLXRecordingExtractor(ap_bin_path)
recording_lf = se.SpikeGLXRecordingExtractor(lf_bin_path)

if stub_test:
    recording_ap = se.SubRecordingExtractor(recording_ap, end_frame=int(nsec_stub*recording_ap.get_sampling_frequency()))
    recording_lf = se.SubRecordingExtractor(recording_lf, end_frame=int(nsec_stub*recording_lf.get_sampling_frequency()))

recording_ap_sync = recording_ap
recording_lf_sync = recording_lf

## 2) Pre-processing
apply_cmr = True

if apply_cmr:
    recording_processed = st.preprocessing.common_reference(recording_ap_sync)
else:
    recording_processed = recording_ap_sync

num_frames = recording_processed.get_num_frames()

## 3) Run spike sorters
sorter_list = [
    "ironclust",
    # "waveclus"
]

# this can also be done by setting global env variables: IRONCLUST_PATH, WAVECLUS_PATH
ss.IronClustSorter.set_ironclust_path("D:/GitHub/ironclust")
ss.WaveClusSorter.set_waveclus_path("D:/GitHub/wave_clus")

# Inspect sorter-specific parameters and defaults
for sorter in sorter_list:
    print(f"{sorter} params description:")
    pprint(ss.get_params_description(sorter))
    print("Default params:")
    pprint(ss.get_default_params(sorter))    

# user-specific parameters
sorter_params = dict(
    kilosort2=dict(car=False),
    ironclust=dict(),
    spykingcircus=dict()
)

sorting_outputs = ss.run_sorters(
    sorter_list=sorter_list, 
    recording_dict_or_list=dict(rec0=recording_ap),
    working_folder=recording_folder / "working",
    mode="keep", # change to "keep" to avoid repeating the spike sorting
    sorter_params=sorter_params
)

## 5) Ensemble spike sorting
# retrieve sortings and sorter names
sorting_list = []
sorter_names_comp = []
for result_name, sorting in sorting_outputs.items():
    rec_name, sorter = result_name
    sorting_list.append(sorting)
    sorter_names_comp.append(sorter)

# run multisorting comparison
mcmp = sc.compare_multiple_sorters(sorting_list=sorting_list, name_list=sorter_names_comp)

# extract ensamble sorting
sorting_ensemble = mcmp.get_agreement_sorting(minimum_agreement_count=1)

# 6) Automatic curation
isi_violation_threshold = 0.5
snr_threshold = 5
firing_rate_threshold = 0.1

sorting_auto_curated = []
sorter_names_curation = []
for result_name, sorting in sorting_outputs.items():
    rec_name, sorter = result_name
    sorter_names_curation.append(sorter)

    # firing rate threshold
    sorting_curated = st.curation.threshold_firing_rates(sorting, duration_in_frames=num_frames,
                                                         threshold=firing_rate_threshold,
                                                         threshold_sign='less')

    # isi violation threshold
    sorting_curated = st.curation.threshold_isi_violations(sorting_curated, duration_in_frames=num_frames,
                                                           threshold=isi_violation_threshold,
                                                           threshold_sign='greater')

    # isi violation threshold
    sorting_curated = st.curation.threshold_snrs(sorting_curated, recording=recording_processed,
                                                 threshold=snr_threshold,
                                                 threshold_sign='less')
    sorting_auto_curated.append(sorting_curated)

# 7) Quick save to NWB; writes only the spikes
# Name your NWBFile and decide where you want it saved
nwbfile_path = "D:/Neuropixels/ActualData/ActualData.nwb"

# Choose the sorting extractor from the notebook environment you would like to write to NWB
chosen_sorting_extractor = sorting_outputs[('rec0', 'ironclust')]

se.NwbSortingExtractor.write_sorting(
    sorting=chosen_sorting_extractor,
    save_path=nwbfile_path,
    overwrite=False,
    skip_properties=['mda_max_channel'],
    skip_features=['waveforms']
)
