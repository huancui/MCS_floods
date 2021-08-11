#!/usr/bin/env python
# coding: utf-8

# ### Script to obtain Episode frequency, and flag with association with MCS or clustered MCS

# In[ ]:


import os
import sys
import numpy as np
from netCDF4 import Dataset
import csv
import string
import datetime
from scipy import stats
from collections import defaultdict
import glob
from datetime import datetime, timedelta, tzinfo

#-----define a few parameters-----
year1        = 2007
year2        = 2018
ydim         = 715
xdim         = 1100
dist_buffer  = 5    # 5*4km=20km
months       = ['04','05','06','07','08']
month_days   = [30, 31, 30, 31, 31, 30]
path1        = '/pic/projects/flood/StageIV_MCS_mask/'
path2        = '/pic/projects/flood/CONUS_simulation/'
path3        = '/pic/projects/flood/MCS_flooding/NOAA_flooding/'
path4        = '/pic/projects/flood/MCS_flooding/NOAA_flooding/StormEvent_extracted/'
path5        = '/pic/projects/flood/MCS_flooding/mcsall/'
path6        = '/pic/projects/flood/MCS_flooding/'
path7        = '/pic/projects/flood/MCS_flooding/mcsclusters/'


# In[ ]:


#-----read in one file to obtain the land mask-----
filename_land = path1 + '20050101_20051231/mcstrack_20050831_1900.nc'
data_land     = Dataset(filename_land, 'r', format='NETCDF4')
precip_land   = data_land.variables['precipitation_st4']
land_mask     = np.where(precip_land[0,:,:] < 1e20, 1, 0)
lat0          = data_land.variables['latitude']
lon0          = data_land.variables['longitude']
lat1          = lat0[:,:]
lon1          = lon0[:,:]

dlat          = lat1[1,0] - lat1[0,0]
dlon          = lon1[0,1] - lon1[0,0]
lat_min       = lat1[0,0] - dlat/2.
lat_max       = lat1[-1,0]+ dlat/2.
lon_min       = lon1[0,0] - dlon/2.
lon_max       = lon1[0,-1]- dlon/2.
print('dlat,dlon,lat_min,lat_max,lon_min,lon_max:', dlat,dlon,lat_min,lat_max,lon_min,lon_max)


# In[ ]:


#-----define functions----
from pytz import timezone
import pytz

def find_stageiv_ij(lat_i, lon_i):
    if (lat_i < lat_min or lat_i > lat_max or lon_i < lon_min or lon_i > lon_max):
        j_out = -1
        i_out = -1
    else:
        j_out = int(np.floor((lat_i-lat_min)/dlat))
        i_out = int(np.floor((lon_i-lon_min)/dlon))
    return j_out, i_out


# In[ ]:


monthstr = ['apr','may','jun','jul','aug']

for iyear in range(year1, year2):
    #----read in MCS time file first----
    filenamem2        = path5 + 'MCS_datetime_all_list_' + str(iyear) +'.dat'
    MCS_datetime_list = []
    f0                = open(filenamem2, 'r')
    for line in f0.readlines():
        line1 = line.strip()
        list  = []
        for num in line1.split(','):
            list.append(num)
        MCS_datetime_list.append(list)
    f0.close()
    #------------------------------------
    filenamem3        = path5 + 'MCS_track_list_' + str(iyear) +'.dat'
    MCS_track_list    = []
    f0        = open(filenamem3, 'r')
    for line in f0.readlines():
        line1 = line.strip()
        MCS_track_list.append(float(line1))
    f0.close()
    #------------------------------------
    filenamem4    = path5 + 'MCS_track_pp' + str(iyear) + '.nc'
    datam4        = Dataset(filenamem4, 'r', format='NETCDF4')       
    mcs_tracks    = datam4.variables['mcs_tracks']
    
    for imonth in range(5):
        episode_frequency_month            = np.zeros((ydim, xdim))
        episode_frequency_month_mcs        = np.zeros((ydim, xdim))
        episode_frequency_month_mcscluster = np.zeros((ydim, xdim))
        type_frequency_month               = np.zeros((3,ydim, xdim))
        type_frequency_month_mcs           = np.zeros((3,ydim, xdim))
        type_frequency_month_mcscluster    = np.zeros((3,ydim, xdim))
        
        filename1  = path4 + 'StormEvent_episodes_info_' + monthstr[imonth]+'_'+str(iyear)+'.csv'
        data1      = np.genfromtxt(filename1, delimiter=',')
        area_flag  = data1[:,10]
        flood_num  = data1[:,1]
        starttime  = data1[:,7]
        endtime    = data1[:,8]
        lat_cen    = data1[:,4]
        lon_cen    = data1[:,5]
        slow_flood = data1[:,2]
        flash_flood= data1[:,3]
        episode_flags = np.zeros((data1.shape[0],2))
        
        filename2  = path4 + 'StormEvent_episodes_'            + monthstr[imonth]+'_'+str(iyear) + '.csv'
        filename3  = path4 + 'StormEvent_episodes_floods_lat_' + monthstr[imonth]+'_'+str(iyear) + '.csv'
        filename4  = path4 + 'StormEvent_episodes_floods_lon_' + monthstr[imonth]+'_'+str(iyear) + '.csv'
        data2      = np.genfromtxt(filename2, delimiter=',')
        data3      = np.genfromtxt(filename3, delimiter=',')
        data4      = np.genfromtxt(filename4, delimiter=',')
        
        for iepi in range(data1.shape[0]):
            j_ind,i_ind = find_stageiv_ij(lat_cen[iepi], lon_cen[iepi])
            if (j_ind >=0 and i_ind >=0):
                episode_frequency_month[j_ind, i_ind] = episode_frequency_month[j_ind, i_ind] +1
                
                #-----set flood type flag----
                flood_type = 0
                if (slow_flood[iepi] >0.5 and flash_flood[iepi]==0):
                    flood_type = 1    # slow-rise
                elif (slow_flood[iepi]==0 and flash_flood[iepi] >0.5):
                    flood_type = 2    # flash
                elif (slow_flood[iepi] >0.5 and flash_flood[iepi] >0.5):
                    flood_type = 3    # hybrid
                if (flood_type > 0.5):
                    type_frequency_month[int(flood_type-1),j_ind,i_ind] = type_frequency_month[int(flood_type-1),j_ind,i_ind] +1
                else:
                    print('flood type invalid.')
                #-----now check if this event is associated with MCS-----
                starttime1 = int(starttime[iepi])
                endtime1   = int(endtime[iepi])
                time_range = np.arange(starttime1, endtime1+1)
                print('time_range:', time_range)
                MCS_match_list  = []
                MCS_match_index = []
                #----loop through MCS time step to see if there's overlap----
                for itime in np.arange(len(time_range)):
                    for imcs in range(len(MCS_datetime_list)):
                        flag_newmcs = 1
                        track_imcs  = MCS_track_list[imcs]
                        steps_inmcs = MCS_datetime_list[imcs]
                        for imcs_step in range(len(steps_inmcs)):
                            if (str(time_range[itime]) == steps_inmcs[imcs_step]):
                                print('find matching step in MCS:', steps_inmcs[imcs_step])
                                if (track_imcs not in MCS_match_list):
                                    MCS_match_list.append(track_imcs)
                                    MCS_match_index.append(imcs)
                #-----now should find all the MCS that overlaps flood duration----
                
                #-----loop through each MCS, check if the location within the MCS area----
                mcs_flag = 0
                if (len(MCS_match_list) > 0):
                    print('found MCS_match_list: ', MCS_match_list)
                    if (flood_num[iepi] > 1):
                        index1     = [j for j in range(len(data2)) if data2[j] == data1[iepi,0]]
                        lats       = data3[index1,:][data3[index1,:] != 0]
                        lons       = data4[index1,:][data4[index1,:] != 0]
                    else:
                        lats       = [lat_cen[iepi]]
                        lons       = [lon_cen[iepi]]
                    print(flood_num[iepi], lats, lons)
                    for iflood in range(len(lats)):
                        j_ind2,i_ind2 = find_stageiv_ij(lats[iflood], lons[iflood])
                        for imcs in range(len(MCS_match_index)):
                            mcs_mask = mcs_tracks[MCS_match_index[imcs], :, :]
                            for jbuff in range(dist_buff*2):
                                for ibuff in range(dist_buff*2):
                                    if (mcs_mask[j_ind2-dist_buff+jbuff, i_ind2-dist_buff+ibuff] > 1.5):
                                        print('Episode within MCS, j,i, MCS[j,i]:', data1[iepi,0], MCS_match_list[imcs], j_ind2, i_ind2, mcs_mask[j_ind2, i_ind2])
                                        mcs_flag = 1
                
                if (mcs_flag > 0.5):
                    episode_frequency_month_mcs[j_ind, i_ind] = episode_frequency_month_mcs[j_ind, i_ind] +1
                    episode_flags[iepi,0]                     = 1
                    type_frequency_month_mcs[int(flood_type-1),j_ind,i_ind] = type_frequency_month_mcs[int(flood_type-1),j_ind,i_ind] +1
                    
    
        #-----output files-----
        outfile1   = path3 + 'OUT/Episode_frequency_'+monthstr[imonth]+'_'+str(iyear)+'.nc'
        rootgrp    =  Dataset(outfile1,'w',format='NETCDF4')
        y1         =  rootgrp.createDimension('y', lon1.shape[0])
        x1         =  rootgrp.createDimension('x', lon1.shape[1])
        t          =  rootgrp.createDimension('t', 3)
        
        latitude   = rootgrp.createVariable('lat','f8',('y','x',))
        latitude.long_name = 'latitude'
        latitude.units     = 'degrees_north'
        latitude[:,:]      = lat1[:,:]

        longitude  = rootgrp.createVariable('lon','f8',('y','x',))
        longitude.longname = 'longitude'
        longitude.units    = 'degrees_east'
        longitude[:,:]     = lon1[:,:]

        freqout1               =  rootgrp.createVariable('episode_frequency','f4',('y','x',))
        freqout1.longname      = 'frequency of floods in each month'
        freqout1.units         = '1'
        freqout1.missing_value = -9.99e5
        freqout1[:,:]          = episode_frequency_month
        
        freqout2               =  rootgrp.createVariable('episode_frequency_mcs','f4',('y','x',))
        freqout2.longname      = 'frequency of floods in each month'
        freqout2.units         = '1'
        freqout2.missing_value = -9.99e5
        freqout2[:,:]          = episode_frequency_month_mcs
        
        freqout4               =  rootgrp.createVariable('type_frequency','f4',('t','y','x',))
        freqout4.longname      = 'frequency of 3 types floods in each month'
        freqout4.units         = '1'
        freqout4.missing_value = -9.99e5
        freqout4[:,:,:]        = type_frequency_month
        
        freqout5               =  rootgrp.createVariable('type_frequency_mcs','f4',('t','y','x',))
        freqout5.longname      = 'frequency of 3 types floods in each month'
        freqout5.units         = '1'
        freqout5.missing_value = -9.99e5
        freqout5[:,:,:]        = type_frequency_month_mcs
        
        rootgrp.close()
        
        #----output matrix----
        outfile2 = path3 + 'OUT/Episode_flags_'+monthstr[imonth]+'_'+str(iyear)+'.csv'
        np.savetxt(outfile2, episode_flags, delimiter=",")
    
    print('year '+ str(iyear)+ ' done.') 
            
              

