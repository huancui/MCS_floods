# Linking flood frequency with Mesoscale Convective Systems
This repository includes the key scripts used by [Hu et al. (2021)](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2021GL092546) to associated floods reported from the NCEI Storm Events Database with mesoscale convective systems (MCSs) in the US. Please find more details about the three python-based scripts below.

Reference: [Hu.H, Feng.Z and L.R.Leung (2021): Linking Flood Frequency with Mesoscale Convective Systems in the US.](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2021GL092546)

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

(*mmm indicates different months from April to August, yyyy indicates different years from 2007-2017)

## 2. Obtain_StormEvent_Episode_MCS.py
This script attributes flood episodes collected by the above "Obtain_StormEvent_Episode_info.py" script to MCS events from the [high-resolution(4km) MCS dataset](https://doi.org/10.5439/1571643). 
### Input files:

### Output files:

## 3. Obtain_StormEvent_Episode_nonMCS.py
This script attribute flood episodes collected by the above "Obtain_StormEvent_Episode_info.py" script to non-MCS rainfall events.
### Input files:
### Output files:

