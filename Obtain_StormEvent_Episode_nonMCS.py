#!/usr/bin/env python
# coding: utf-8

# ### Script to obtain Episode frequency associated with non-MCS rainfall

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
dist_buffer  = 5       #20km
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


#-----define functions-----

def find_stageiv_ij(lat_i, lon_i):
    if (lat_i < lat_min or lat_i > lat_max or lon_i < lon_min or lon_i > lon_max):
        j_out = -1
        i_out = -1
    else:
        j_out = int(np.floor((lat_i-lat_min)/dlat))
        i_out = int(np.floor((lon_i-lon_min)/dlon))
    return j_out, i_out

def get_timeranges(time1, time2):
    time1_str = datetime.strptime(str(time1),'%Y%m%d%H')
    time2_str = datetime.strptime(str(time2),'%Y%m%d%H')
    delta_hours = (time2_str - time1_str).days*24+(time2_str - time1_str).seconds/3600
    time_list = []
    for ihour in range(int(delta_hours+1)):
        time_list.append((time1_str+timedelta(hours=ihour)).strftime('%Y%m%d_%H00'))
    return time_list


# In[ ]:


monthstr = ['apr','may','jun','jul','aug']

for iyear in range(year1, year2):
    
    for imonth in range(5):
        episode_frequency_month_nonmcs        = np.zeros((ydim, xdim))
        type_frequency_month_nonmcs           = np.zeros((3,ydim, xdim))
        
        #-----read in Episode_flag files-----
        filenamef1      = path3 + 'OUT/Episode_flags_'+monthstr[imonth]+'_'+str(iyear)+'.csv'
        episode_flags   = np.genfromtxt(filenamef1, delimiter=',')
        episode_flags2  = np.zeros(episode_flags.shape)
        
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
        
        filename2  = path4 + 'StormEvent_episodes_'            + monthstr[imonth]+'_'+str(iyear) + '.csv'
        filename3  = path4 + 'StormEvent_episodes_floods_lat_' + monthstr[imonth]+'_'+str(iyear) + '.csv'
        filename4  = path4 + 'StormEvent_episodes_floods_lon_' + monthstr[imonth]+'_'+str(iyear) + '.csv'
        data2      = np.genfromtxt(filename2, delimiter=',')
        data3      = np.genfromtxt(filename3, delimiter=',')
        data4      = np.genfromtxt(filename4, delimiter=',')
        
        for iepi in range(data1.shape[0]):
            if (episode_flags[iepi,0] < 0.5):    #flood episode is not associated with MCS
                j_ind,i_ind = find_stageiv_ij(lat_cen[iepi], lon_cen[iepi])
                if (j_ind >= 0 and i_ind >= 0):
                    #-----set flood type flag----
                    flood_type = 0
                    if (slow_flood[iepi] >0.5 and flash_flood[iepi]==0):
                        flood_type = 1    # slow-rise
                    elif (slow_flood[iepi]==0 and flash_flood[iepi] >0.5):
                        flood_type = 2    # flash
                    elif (slow_flood[iepi] >0.5 and flash_flood[iepi] >0.5):
                        flood_type = 3    # hybrid
                
                    #-----check if this event is associated with non-MCS rainfall-----
                    starttime1 = int(starttime[iepi])
                    endtime1   = int(endtime[iepi])
                    time_range = get_timeranges(starttime1, endtime1)
                    print('time_range:', time_range)
                
                    #----get the boundary of locations-----
                    if (flood_num[iepi] > 1):
                        index1     = [j for j in range(len(data2)) if data2[j] == data1[iepi,0]]
                        lats       = data3[index1,:][data3[index1,:] != 0]
                        lons       = data4[index1,:][data4[index1,:] != 0]
                    else:
                        lats       = [lat_cen[iepi]]
                        lons       = [lon_cen[iepi]]
                    print(flood_num[iepi], lats, lons, j_ind, i_ind)
                    lat_min2 = min(lats)
                    lat_max2 = max(lats)
                    lon_min2 = min(lons)
                    lon_max2 = max(lons)
                    print('lat_min, lat_max, lon_min, lon_max:',lat_min2, lat_max2, lon_min2, lon_max2)
                    j_min,i_min = find_stageiv_ij(lat_min2, lon_min2)
                    j_max,i_max = find_stageiv_ij(lat_max2, lon_max2)
                    if (j_min<0 and i_min<0):
                        j_min   = j_max
                        i_min   = i_max
                    if (j_max<0 and i_max<0):
                        j_max   = j_min
                        i_max   = i_min
                    j_min2      = max(0, j_min-dist_buffer)    
                    j_max2      = min(ydim,j_max+dist_buffer+1)
                    i_min2      = max(0, i_min-dist_buffer)
                    i_max2      = min(xdim,i_max+dist_buffer+1)
                    print('j_min,j_max,i_min,i_max,j_min2,j_max2,i_min2,i_max2:',j_min,j_max,i_min,i_max,j_min2,j_max2,i_min2,i_max2)

                    #----loop through each time step in time_range-----
                    mcs_flag    = 0
                    nonmcs_flag = 0
                    for itime in range(len(time_range)):
                        filename_stageiv = path1 + str(iyear) +'0101_' + str(iyear) +'1231/mcstrack_' + time_range[itime] +'.nc'
                        if os.path.isfile(filename_stageiv):
                            data_stageiv    = Dataset(filename_stageiv, 'r', format='NETCDF4')
                            precip_stageiv  = data_stageiv.variables['precipitation_st4']
                            mcsmask_stageiv = data_stageiv.variables['pcptracknumber']
                            #---crop over the range----
                            precip_box      = precip_stageiv[0,j_min2:j_max2,i_min2:i_max2]
                            mcsmask_box     = mcsmask_stageiv[0,j_min2:j_max2,i_min2:i_max2]
                            if (np.max(precip_box) >0.1 and np.max(precip_box)<1e20):  # there is precip
                                if (np.max(mcsmask_box) > 1):   #MCS rainfall exist in this box
                                    mcs_flag = 1
                                else:
                                    nonmcs_flag = 1
                        else:
                            print('file does not exit:', filename_stageiv)

                    #----assign these flags----
                    episode_flags2[iepi,0] = mcs_flag
                    episode_flags2[iepi,1] = nonmcs_flag

                    if (nonmcs_flag > 0.5):
                        episode_frequency_month_nonmcs[j_ind,i_ind] = episode_frequency_month_nonmcs[j_ind, i_ind] +1
                        type_frequency_month_nonmcs[int(flood_type-1),j_ind,i_ind] = type_frequency_month_nonmcs[int(flood_type-1),j_ind,i_ind] +1

        #-----output files-----
        outfile1   = path3 + 'OUT/Episode_frequency_'+monthstr[imonth]+'_'+str(iyear)+'nonMCS.nc'
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
        freqout1[:,:]          = episode_frequency_month_nonmcs
        
        freqout4               =  rootgrp.createVariable('type_frequency','f4',('t','y','x',))
        freqout4.longname      = 'frequency of 3 types floods in each month'
        freqout4.units         = '1'
        freqout4.missing_value = -9.99e5
        freqout4[:,:,:]        = type_frequency_month_nonmcs
        
        rootgrp.close()
        
        #----output matrix----
        outfile2 = path3 + 'OUT/Episode_flags_'+monthstr[imonth]+'_'+str(iyear)+'nonmcs.csv'
        np.savetxt(outfile2, episode_flags2, delimiter=",")
        
    print('year '+ str(iyear)+ ' done.')
                
                    


# In[ ]:




