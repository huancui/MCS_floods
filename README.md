# Linking flood frequency with Mesoscale Convective Systems
This repository includes the key scripts used by [Hu et al. (2021)](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2021GL092546) to associated floods reported from the NCEI Storm Events Database with mesoscale convective systems (MCSs) in the US. Please find more details about the three python-based scripts below.

Reference: [Hu.H, Feng.Z and L.R.Leung (2021): Linking Flood Frequency with Mesoscale Convective Systems in the US.](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2021GL092546)

1. Obtain_StormEvent_Episode_info.py
2. Obtain_StormEvent_Episode_MCS.py
3. Obtain_StormEvent_Episode_nonMCS.py

## 1. Obtain_StormEvent_Episode_info.py
This script collects the information (e.g. timing, location, duration) of each flood episode, which might consist of multiple flood events, as a preperation for the following analysis to be linked with MCS or non-MCS storms. Note that floods in April-August 2007-2017 are of our interest. 
### Input files:
|  | File names | Description |
| ----- | ------ | ------ |
| A	| StormEvents_details-ftp_v1.0_dyyyy_c*.csv | details and descriptions of each Storm Event |
| B | StormEvents_locations-ftp_v1.0_dyyyy_c*.csv | locations of each Storm Event |

(*yyyy indicates each year. The Storm Event database can be downloaded from ftp://ftp.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/)

### Output files:
|  | File names | Description |
| ------ | ------ | ------ |
| A	| StormEvent_episodes_mmm_yyyy.csv | list of flood episodes in each month|
| B | StormEvent_episodes_floods_lat_mmm_yyyy.csv | latitudes of each flood event (columns) belonging to each flood episode (rows) |
| C | StormEvent_episodes_floods_lon_mmm_yyyy.csv | longitudes of each flood event (columns) belonging to each flood episode (rows) |
| D | StormEvent_episodes_floods_time1_mmm_yyyy.csv | starting times of each flood event (columns) belonging to each flood episode (rows) |
| E | StormEvent_episodes_floods_time2_mmm_yyyy.csv | ending times of each flood event (columns) belonging to each flood episode (rows) |
| F | StormEvent_episodes_floods_type_mmm_yyyy.csv | flood types of each flood event (columns) belonging to each flood episode (rows): 1->slow-rising flood, 2->flash flood |
| G | StormEvent_episodes_info_mmm_yyyy.csv | gather all the above information of flood episodes into one file |

(*mmm indicates different months from April to August, yyyy indicates different years from 2007-2017)

## 2. Obtain_StormEvent_Episode_MCS.py
This script attributes flood episodes collected by the above "Obtain_StormEvent_Episode_info.py" script to MCS events from the [high-resolution(4km) MCS dataset](https://doi.org/10.5439/1571643). 
### Input files:
|  | File names | Description |
| ----- | ------ | ------ |
| A	| StormEvent_episodes_info_mmm_yyyy.csv | information of each flood episode (output from "Obtain_StormEvent_Episode_info.py") |
| B | StormEvent_episodes_mmm_yyyy.csv | list of flood episodes in each month (output from "Obtain_StormEvent_Episode_info.py") |
| C | StormEvent_episodes_floods_lat_mmm_yyyy.csv | latitudes of each flood event (columns) belonging to each flood episode (rows)(output from "Obtain_StormEvent_Episode_info.py") |
| D | StormEvent_episodes_floods_lon_mmm_yyyy.csv | longitudes of each flood event (columns) belonging to each flood episode (rows)(output from "Obtain_StormEvent_Episode_info.py") |
| E | MCS_track_ppyyyy.nc | MCS tracks and precipitation data processed from [4-km MCS dataset](https://doi.org/10.5439/1571643) |
| F | MCS_track_list_yyyy.dat | list of MCS track IDs that matches the IDs in "MCS_track_ppyyyy.nc" files |
| G | MCS_datetime_all_list_yyyy.dat | list of timesteps within the lifetime of each MCS |

(* note that files E-F are not directly available for downloading from the ARM website, pre-processing might be necessary. Please contact us if help is needed.)

### Output files:
|  | File names | Description |
| ----- | ------ | ------ |
| A	| Episode_frequency_mmm_yyyy.nc | maps of flood episode frequency and MCS-related floods in each month |
| B | Episode_flags_mmm_yyyy.csv | list of flags for flood episodes indicating whether a flood is associated with MCS or not: first column 1->associated with MCS; 0-> not associated with MCS |

## 3. Obtain_StormEvent_Episode_nonMCS.py
This script attribute flood episodes collected by the above "Obtain_StormEvent_Episode_info.py" script to non-MCS rainfall events.
### Input files:
|  | File names | Description |
| ----- | ------ | ------ |
| A	| Episode_flags_mmm_yyyy.csv | list of flags for flood episodes indicating whether a flood is associated with MCS or not (output from "Obtain_StormEvent_Episode_MCS.py") |
| B | StormEvent_episodes_info_mmm_yyyy.csv | information of each flood episode (output from "Obtain_StormEvent_Episode_info.py") |
| C | StormEvent_episodes_mmm_yyyy.csv | list of flood episodes in each month (output from "Obtain_StormEvent_Episode_info.py") |
| D | StormEvent_episodes_floods_lat_mmm_yyyy.csv | latitudes of each flood event (columns) belonging to each flood episode (rows)(output from "Obtain_StormEvent_Episode_info.py") |
| E | StormEvent_episodes_floods_lon_mmm_yyyy.csv | longitudes of each flood event (columns) belonging to each flood episode (rows)(output from "Obtain_StormEvent_Episode_info.py") |
| F | yyyy0101_yyyy1231/mcstrack_%Y%m%d_%H00.nc | [4-km MCS dataset](https://doi.org/10.5439/1571643) |

### Output files:
|  | File names | Description |
| ----- | ------ | ------ |
| A	| Episode_frequency_mmm_yyyynonMCS.nc | maps of non-MCS-related flood episode frequency in each month |
| B | Episode_flags_mmm_yyyynonmcs.csv | list of flags for flood episodes indicating whether a flood is associated with non-MCS storms or not: second column 1->associated with non-MCS rainfall; 0-> not associated with non-MCS rainfall |



