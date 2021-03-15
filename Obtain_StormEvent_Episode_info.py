#!/usr/bin/env python
# coding: utf-8

# ### Script to group flooding events inot episodes

# In[17]:


import os
import sys
import numpy as np
# from netCDF4 import Dataset
import csv
import string
import datetime
from scipy import stats
from collections import defaultdict
import glob
from datetime import datetime, timedelta, tzinfo
from pyproj import Proj
from shapely.geometry import shape

#-----define a few parameters-----
year1        = 2007
year2        = 2018
ydim         = 715
xdim         = 1100
months       = ['04','05','06','07','08']
month_days   = [30, 31, 30, 31, 31, 30]

path1 = '/Users/huhu962/Desktop/CONUS_simulation/MCS_flooding/'
path3 = path1 + 'NOAA_flooding/'

lat_min = 25
lat_max = 51
lon_min = -110
lon_max = -70


# In[18]:


#-----define functions----
from pytz import timezone
import pytz

class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
            return timedelta(hours=1) if self.isdst else timedelta(0)
    def tzname(self,dt):
         return self.name

def get_hour_utc(t1):
    t1utc = t1.astimezone(pytz.utc)
    return t1utc.strftime('%Y%m%d%H')

def find_hour_offset(zonex):
    if (zonex == 'EST'):
        hour_int = -5
    elif (zonex == 'CST'):
        hour_int = -6
    elif (zonex == 'MST'):
        hour_int = -7
    elif (zonex == 'PST'):
        hour_int = -8
    else:
        hour_int = 1
    return hour_int

def count_hours(time1, time2):
    time1_str = str(int(time1))
    time2_str = str(int(time2))
    time1_date = datetime.strptime(time1_str, '%Y%m%d%H')
    time2_date = datetime.strptime(time2_str, '%Y%m%d%H')
    return (time2_date-time1_date).days*24+(time2_date-time1_date).seconds/3600

def sortVertices(list1, list2):
    center_xc = np.sum(list1)/list1.shape 
    center_yr = np.sum(list2)/list1.shape 
    theta = np.arctan2(list2-center_yr, list1-center_xc) * 180 / np.pi
    indices = np.argsort(theta)
    x = list1[indices]
    y = list2[indices]
    return x, y


# In[19]:


#----loop through each year------
for iyear in range(year1, year2):
    filelist1 = [f for f in glob.glob(path3 + "StormEvents_details-ftp_v1.0_d"+str(iyear)+'_c*.csv')]
    filelist2 = [f for f in glob.glob(path3 + "StormEvents_locations-ftp_v1.0_d"+str(iyear)+'_c*.csv')]
    print(filelist1)
    print(filelist2)
    filename1 = filelist1[0]
    filename2 = filelist2[0]
    #----read in detail file----
    columns = defaultdict(list)
    with open(filename1) as f:
        reader = csv.DictReader(f)
        for row in reader:
            for (k,v) in row.items():
                columns[k].append(v)
    f.close
    columns_loc = defaultdict(list)
    with open(filename2) as f:
        reader = csv.DictReader(f)
        for row in reader:
            for (k,v) in row.items():
                columns_loc[k].append(v)
    f.close
    #-----loop through to find flood events-----
    episode_apr = []
    episode_may = []
    episode_jun = []
    episode_jul = []
    episode_aug = []
    episode_flood_apr = []
    episode_flood_may = []
    episode_flood_jun = []
    episode_flood_jul = []
    episode_flood_aug = []
    
    for i in range(len(columns['BEGIN_YEARMONTH'])):
        if (columns['EVENT_TYPE'][i] == 'Flood' or columns['EVENT_TYPE'][i] == 'Flash Flood'):
            episode_i = columns['EPISODE_ID'][i]
            if int(columns['BEGIN_YEARMONTH'][i][4:6]) == 4:
                if episode_i not in episode_apr:
                    episode_apr.append(episode_i)
                    episode_flood_apr.append([columns['EVENT_ID'][i]])
                else:
                    ilist = episode_apr.index(episode_i)
                    episode_flood_apr[ilist].append(columns['EVENT_ID'][i])
            elif int(columns['BEGIN_YEARMONTH'][i][4:6]) == 5:
                if episode_i not in episode_may:
                    episode_may.append(episode_i)
                    episode_flood_may.append([columns['EVENT_ID'][i]])
                else:
                    ilist = episode_may.index(episode_i)
                    episode_flood_may[ilist].append(columns['EVENT_ID'][i])
            elif int(columns['BEGIN_YEARMONTH'][i][4:6]) == 6:
                if episode_i not in episode_jun:
                    episode_jun.append(episode_i)
                    episode_flood_jun.append([columns['EVENT_ID'][i]])
                else:
                    ilist = episode_jun.index(episode_i)
                    episode_flood_jun[ilist].append(columns['EVENT_ID'][i])
            elif int(columns['BEGIN_YEARMONTH'][i][4:6]) == 7:
                if episode_i not in episode_jul:
                    episode_jul.append(episode_i)
                    episode_flood_jul.append([columns['EVENT_ID'][i]])
                else:
                    ilist = episode_jul.index(episode_i)
                    episode_flood_jul[ilist].append(columns['EVENT_ID'][i])
            elif int(columns['BEGIN_YEARMONTH'][i][4:6]) == 8:
                if episode_i not in episode_aug:
                    episode_aug.append(episode_i)
                    episode_flood_aug.append([columns['EVENT_ID'][i]])
                else:
                    ilist = episode_aug.index(episode_i)
                    episode_flood_aug[ilist].append(columns['EVENT_ID'][i])
                    
    print('len(episode_apr), len(episode_flood_apr):',len(episode_apr), len(episode_flood_apr))
    print('len(episode_may), len(episode_flood_may):',len(episode_may), len(episode_flood_may))
    print('len(episode_jun), len(episode_flood_jun):',len(episode_jun), len(episode_flood_jun))
    print('len(episode_jul), len(episode_flood_jul):',len(episode_jul), len(episode_flood_jul))
    print('len(episode_aug), len(episode_flood_aug):',len(episode_aug), len(episode_flood_aug))
    
    
    #-----create matrix to save flood information for each episode-----
    flood_size = 0
    for ii in range(len(episode_apr)):
        if (flood_size < len(episode_flood_apr[ii])):
            flood_size = len(episode_flood_apr[ii])
    episode_matrix_apr      = np.zeros(len(episode_apr))
    episode_flood_matrix_apr= np.zeros((len(episode_apr), flood_size))
    episode_flood_lat_apr   = np.zeros((len(episode_apr), flood_size))
    episode_flood_lon_apr   = np.zeros((len(episode_apr), flood_size))
    episode_flood_time1_apr = np.zeros((len(episode_apr), flood_size))
    episode_flood_time2_apr = np.zeros((len(episode_apr), flood_size))
    episode_flood_type_apr  = np.zeros((len(episode_apr), flood_size))
    for ii in range(len(episode_apr)):
        episode_ii = episode_apr[ii]
        episode_matrix_apr[ii] = episode_ii
        for jj in range(len(episode_flood_apr[ii])):
            flood_jj   = episode_flood_apr[ii][jj]
            episode_flood_matrix_apr[ii,jj] = flood_jj
            #-----find lat and lon info-----
            index1     = [j for j in range(len(columns_loc['EVENT_ID'])) if columns_loc['EVENT_ID'][j] == flood_jj]
            if not index1:
                print("EVENT NOT FOUND.")
            else:
                # get an average if multiple locations are found
                sumlat = 0.0
                sumlon = 0.0
                index2 = 0.0
                j_ind  = -1
                i_ind  = -1
                for k in index1:
                    if (not columns_loc['LATITUDE'][k] or not columns_loc['LONGITUDE'][k]):
                        print('no latitude/longitude for this event: ', flood_jj)
                    else:
                        index2 = index2+1
                        sumlat = sumlat + float(columns_loc['LATITUDE'][k])
                        sumlon = sumlon + float(columns_loc['LONGITUDE'][k])
                if (index2 <= 0):
                    print('index2 <= 0 ')
                else:
                    lat_eventx = sumlat/index2
                    lon_eventx = sumlon/index2
                    if (lat_eventx >= lat_min and lat_eventx <= lat_max and lon_eventx >= lon_min and lon_eventx <= lon_max):
                        episode_flood_lat_apr[ii,jj] = lat_eventx
                        episode_flood_lon_apr[ii,jj] = lon_eventx
                    
                        #-----find flood type-----
                        index3     = [j for j in range(len(columns['EVENT_ID'])) if columns['EVENT_ID'][j] == flood_jj]
            #             print('len(index3), index3:', len(index3), index3)
                        if (columns['EVENT_TYPE'][index3[0]] == 'Flood'):
                            episode_flood_type_apr[ii,jj] = 1
                        elif (columns['EVENT_TYPE'][index3[0]] == 'Flash Flood'):
                            episode_flood_type_apr[ii,jj] = 2

                        #-----find time information-----
                        begin_time = columns['BEGIN_DATE_TIME'][index3[0]]
                        end_time   = columns['END_DATE_TIME'][index3[0]]
                        if (len(columns['CZ_TIMEZONE'][index3[0]]) < 4):
                            time_zone_int = find_hour_offset(columns['CZ_TIMEZONE'][index3[0]][0:3])
                        else:
                            time_zone_int = int(columns['CZ_TIMEZONE'][index3[0]][3:5])
                        if (time_zone_int < 0):
                            gettz          = Zone(time_zone_int,False,columns['CZ_TIMEZONE'][index3[0]][0:3])
                            time_start     = datetime.strptime(columns['BEGIN_DATE_TIME'][index3[0]],'%d-%b-%y %H:%M:%S').replace(tzinfo=gettz)
                            time_end       = datetime.strptime(columns['END_DATE_TIME'][index3[0]],'%d-%b-%y %H:%M:%S').replace(tzinfo=gettz)
                            time_start_utc = get_hour_utc(time_start)
                            time_end_utc   = get_hour_utc(time_end)
                            episode_flood_time1_apr[ii,jj] = int(time_start_utc)
                            episode_flood_time2_apr[ii,jj] = int(time_end_utc)
                        else:
                            print('time_zone_int > 0: ', columns['CZ_TIMEZONE'][index3[0]][0:3], time_zone_int)

    #-----output matrix variables-----
    outfile1 = path1 + 'StormEvent_episodes_apr_'+str(iyear)+'.csv'
    outfile2 = path1 + 'StormEvent_episodes_floods_apr_'+str(iyear)+'.csv'
    outfile3 = path1 + 'StormEvent_episodes_floods_lat_apr_'+str(iyear)+'.csv'
    outfile4 = path1 + 'StormEvent_episodes_floods_lon_apr_'+str(iyear)+'.csv'
    outfile5 = path1 + 'StormEvent_episodes_floods_time1_apr_'+str(iyear)+'.csv'
    outfile6 = path1 + 'StormEvent_episodes_floods_time2_apr_'+str(iyear)+'.csv'
    outfile7 = path1 + 'StormEvent_episodes_floods_type_apr_'+str(iyear)+'.csv'
    np.savetxt(outfile1, episode_matrix_apr, delimiter=",")
    np.savetxt(outfile2, episode_flood_matrix_apr, delimiter=",")
    np.savetxt(outfile3, episode_flood_lat_apr, delimiter=",")
    np.savetxt(outfile4, episode_flood_lon_apr, delimiter=",")
    np.savetxt(outfile5, episode_flood_time1_apr, delimiter=",")
    np.savetxt(outfile6, episode_flood_time2_apr, delimiter=",")
    np.savetxt(outfile7, episode_flood_type_apr, delimiter=",")
    


    #-----repeat for may-----
    flood_size = 0
    for ii in range(len(episode_may)):
        if (flood_size < len(episode_flood_may[ii])):
            flood_size = len(episode_flood_may[ii])
    episode_matrix_may      = np.zeros(len(episode_may))
    episode_flood_matrix_may= np.zeros((len(episode_may), flood_size))
    episode_flood_lat_may   = np.zeros((len(episode_may), flood_size))
    episode_flood_lon_may   = np.zeros((len(episode_may), flood_size))
    episode_flood_time1_may = np.zeros((len(episode_may), flood_size))
    episode_flood_time2_may = np.zeros((len(episode_may), flood_size))
    episode_flood_type_may  = np.zeros((len(episode_may), flood_size))
    for ii in range(len(episode_may)):
        episode_ii = episode_may[ii]
        episode_matrix_may[ii] = episode_ii
        for jj in range(len(episode_flood_may[ii])):
            flood_jj   = episode_flood_may[ii][jj]
            episode_flood_matrix_may[ii,jj] = flood_jj
            #-----find lat and lon info-----
            index1     = [j for j in range(len(columns_loc['EVENT_ID'])) if columns_loc['EVENT_ID'][j] == flood_jj]
            if not index1:
                print("EVENT NOT FOUND.")
            else:
                # get an average if multiple locations are found
                sumlat = 0.0
                sumlon = 0.0
                index2 = 0.0
                j_ind  = -1
                i_ind  = -1
                for k in index1:
                    if (not columns_loc['LATITUDE'][k] or not columns_loc['LONGITUDE'][k]):
                        print('no latitude/longitude for this event: ', flood_jj)
                    else:
                        index2 = index2+1
                        sumlat = sumlat + float(columns_loc['LATITUDE'][k])
                        sumlon = sumlon + float(columns_loc['LONGITUDE'][k])
                if (index2 <= 0):
                    print('index2 <= 0 ')
                else:
                    lat_eventx = sumlat/index2
                    lon_eventx = sumlon/index2
                    if (lat_eventx >= lat_min and lat_eventx <= lat_max and lon_eventx >= lon_min and lon_eventx <= lon_max):
                        episode_flood_lat_may[ii,jj] = lat_eventx
                        episode_flood_lon_may[ii,jj] = lon_eventx
                    
                        #-----find flood type-----
                        index3     = [j for j in range(len(columns['EVENT_ID'])) if columns['EVENT_ID'][j] == flood_jj]
            #             print('len(index3), index3:', len(index3), index3)
                        if (columns['EVENT_TYPE'][index3[0]] == 'Flood'):
                            episode_flood_type_may[ii,jj] = 1
                        elif (columns['EVENT_TYPE'][index3[0]] == 'Flash Flood'):
                            episode_flood_type_may[ii,jj] = 2

                        #-----find time information-----
                        begin_time = columns['BEGIN_DATE_TIME'][index3[0]]
                        end_time   = columns['END_DATE_TIME'][index3[0]]
                        if (len(columns['CZ_TIMEZONE'][index3[0]]) < 4):
                            time_zone_int = find_hour_offset(columns['CZ_TIMEZONE'][index3[0]][0:3])
                        else:
                            time_zone_int = int(columns['CZ_TIMEZONE'][index3[0]][3:5])
                        if (time_zone_int < 0):
                            gettz          = Zone(time_zone_int,False,columns['CZ_TIMEZONE'][index3[0]][0:3])
                            time_start     = datetime.strptime(columns['BEGIN_DATE_TIME'][index3[0]],'%d-%b-%y %H:%M:%S').replace(tzinfo=gettz)
                            time_end       = datetime.strptime(columns['END_DATE_TIME'][index3[0]],'%d-%b-%y %H:%M:%S').replace(tzinfo=gettz)
                            time_start_utc = get_hour_utc(time_start)
                            time_end_utc   = get_hour_utc(time_end)
                            episode_flood_time1_may[ii,jj] = int(time_start_utc)
                            episode_flood_time2_may[ii,jj] = int(time_end_utc)
                        else:
                            print('time_zone_int > 0: ', columns['CZ_TIMEZONE'][index3[0]][0:3], time_zone_int)

    #-----output matrix variables-----
    outfile1 = path1 + 'StormEvent_episodes_may_'+str(iyear)+'.csv'
    outfile2 = path1 + 'StormEvent_episodes_floods_may_'+str(iyear)+'.csv'
    outfile3 = path1 + 'StormEvent_episodes_floods_lat_may_'+str(iyear)+'.csv'
    outfile4 = path1 + 'StormEvent_episodes_floods_lon_may_'+str(iyear)+'.csv'
    outfile5 = path1 + 'StormEvent_episodes_floods_time1_may_'+str(iyear)+'.csv'
    outfile6 = path1 + 'StormEvent_episodes_floods_time2_may_'+str(iyear)+'.csv'
    outfile7 = path1 + 'StormEvent_episodes_floods_type_may_'+str(iyear)+'.csv'
    np.savetxt(outfile1, episode_matrix_may, delimiter=",")
    np.savetxt(outfile2, episode_flood_matrix_may, delimiter=",")
    np.savetxt(outfile3, episode_flood_lat_may, delimiter=",")
    np.savetxt(outfile4, episode_flood_lon_may, delimiter=",")
    np.savetxt(outfile5, episode_flood_time1_may, delimiter=",")
    np.savetxt(outfile6, episode_flood_time2_may, delimiter=",")
    np.savetxt(outfile7, episode_flood_type_may, delimiter=",")
    

    #-----repeat for june-----
    flood_size = 0
    for ii in range(len(episode_jun)):
        if (flood_size < len(episode_flood_jun[ii])):
            flood_size = len(episode_flood_jun[ii])
    episode_matrix_jun      = np.zeros(len(episode_jun))
    episode_flood_matrix_jun= np.zeros((len(episode_jun), flood_size))
    episode_flood_lat_jun   = np.zeros((len(episode_jun), flood_size))
    episode_flood_lon_jun   = np.zeros((len(episode_jun), flood_size))
    episode_flood_time1_jun = np.zeros((len(episode_jun), flood_size))
    episode_flood_time2_jun = np.zeros((len(episode_jun), flood_size))
    episode_flood_type_jun  = np.zeros((len(episode_jun), flood_size))
    for ii in range(len(episode_jun)):
        episode_ii = episode_jun[ii]
        episode_matrix_jun[ii] = episode_ii
        for jj in range(len(episode_flood_jun[ii])):
            flood_jj   = episode_flood_jun[ii][jj]
            episode_flood_matrix_jun[ii,jj] = flood_jj
            #-----find lat and lon info-----
            index1     = [j for j in range(len(columns_loc['EVENT_ID'])) if columns_loc['EVENT_ID'][j] == flood_jj]
            if not index1:
                print("EVENT NOT FOUND.")
            else:
                # get an average if multiple locations are found
                sumlat = 0.0
                sumlon = 0.0
                index2 = 0.0
                j_ind  = -1
                i_ind  = -1
                for k in index1:
                    if (not columns_loc['LATITUDE'][k] or not columns_loc['LONGITUDE'][k]):
                        print('no latitude/longitude for this event: ', flood_jj)
                    else:
                        index2 = index2+1
                        sumlat = sumlat + float(columns_loc['LATITUDE'][k])
                        sumlon = sumlon + float(columns_loc['LONGITUDE'][k])
                if (index2 <= 0):
                    print('index2 <= 0 ')
                else:
                    lat_eventx = sumlat/index2
                    lon_eventx = sumlon/index2
                    if (lat_eventx >= lat_min and lat_eventx <= lat_max and lon_eventx >= lon_min and lon_eventx <= lon_max):
                        episode_flood_lat_jun[ii,jj] = lat_eventx
                        episode_flood_lon_jun[ii,jj] = lon_eventx
                    
                        #-----find flood type-----
                        index3     = [j for j in range(len(columns['EVENT_ID'])) if columns['EVENT_ID'][j] == flood_jj]
            #             print('len(index3), index3:', len(index3), index3)
                        if (columns['EVENT_TYPE'][index3[0]] == 'Flood'):
                            episode_flood_type_jun[ii,jj] = 1
                        elif (columns['EVENT_TYPE'][index3[0]] == 'Flash Flood'):
                            episode_flood_type_jun[ii,jj] = 2

                        #-----find time information-----
                        begin_time = columns['BEGIN_DATE_TIME'][index3[0]]
                        end_time   = columns['END_DATE_TIME'][index3[0]]
                        if (len(columns['CZ_TIMEZONE'][index3[0]]) < 4):
                            time_zone_int = find_hour_offset(columns['CZ_TIMEZONE'][index3[0]][0:3])
                        else:
                            time_zone_int = int(columns['CZ_TIMEZONE'][index3[0]][3:5])
                        if (time_zone_int < 0):
                            gettz          = Zone(time_zone_int,False,columns['CZ_TIMEZONE'][index3[0]][0:3])
                            time_start     = datetime.strptime(columns['BEGIN_DATE_TIME'][index3[0]],'%d-%b-%y %H:%M:%S').replace(tzinfo=gettz)
                            time_end       = datetime.strptime(columns['END_DATE_TIME'][index3[0]],'%d-%b-%y %H:%M:%S').replace(tzinfo=gettz)
                            time_start_utc = get_hour_utc(time_start)
                            time_end_utc   = get_hour_utc(time_end)
                            episode_flood_time1_jun[ii,jj] = int(time_start_utc)
                            episode_flood_time2_jun[ii,jj] = int(time_end_utc)
                        else:
                            print('time_zone_int > 0: ', columns['CZ_TIMEZONE'][index3[0]][0:3], time_zone_int)

    #-----output matrix variables-----
    outfile1 = path1 + 'StormEvent_episodes_jun_'+str(iyear)+'.csv'
    outfile2 = path1 + 'StormEvent_episodes_floods_jun_'+str(iyear)+'.csv'
    outfile3 = path1 + 'StormEvent_episodes_floods_lat_jun_'+str(iyear)+'.csv'
    outfile4 = path1 + 'StormEvent_episodes_floods_lon_jun_'+str(iyear)+'.csv'
    outfile5 = path1 + 'StormEvent_episodes_floods_time1_jun_'+str(iyear)+'.csv'
    outfile6 = path1 + 'StormEvent_episodes_floods_time2_jun_'+str(iyear)+'.csv'
    outfile7 = path1 + 'StormEvent_episodes_floods_type_jun_'+str(iyear)+'.csv'
    np.savetxt(outfile1, episode_matrix_jun, delimiter=",")
    np.savetxt(outfile2, episode_flood_matrix_jun, delimiter=",")
    np.savetxt(outfile3, episode_flood_lat_jun, delimiter=",")
    np.savetxt(outfile4, episode_flood_lon_jun, delimiter=",")
    np.savetxt(outfile5, episode_flood_time1_jun, delimiter=",")
    np.savetxt(outfile6, episode_flood_time2_jun, delimiter=",")
    np.savetxt(outfile7, episode_flood_type_jun, delimiter=",")
    

    #-----repeat for july-----
    flood_size = 0
    for ii in range(len(episode_jul)):
        if (flood_size < len(episode_flood_jul[ii])):
            flood_size = len(episode_flood_jul[ii])
    episode_matrix_jul      = np.zeros(len(episode_jul))
    episode_flood_matrix_jul= np.zeros((len(episode_jul), flood_size))
    episode_flood_lat_jul   = np.zeros((len(episode_jul), flood_size))
    episode_flood_lon_jul   = np.zeros((len(episode_jul), flood_size))
    episode_flood_time1_jul = np.zeros((len(episode_jul), flood_size))
    episode_flood_time2_jul = np.zeros((len(episode_jul), flood_size))
    episode_flood_type_jul  = np.zeros((len(episode_jul), flood_size))
    for ii in range(len(episode_jul)):
        episode_ii = episode_jul[ii]
        episode_matrix_jul[ii] = episode_ii
        for jj in range(len(episode_flood_jul[ii])):
            flood_jj   = episode_flood_jul[ii][jj]
            episode_flood_matrix_jul[ii,jj] = flood_jj
            #-----find lat and lon info-----
            index1     = [j for j in range(len(columns_loc['EVENT_ID'])) if columns_loc['EVENT_ID'][j] == flood_jj]
            if not index1:
                print("EVENT NOT FOUND.")
            else:
                # get an average if multiple locations are found
                sumlat = 0.0
                sumlon = 0.0
                index2 = 0.0
                j_ind  = -1
                i_ind  = -1
                for k in index1:
                    if (not columns_loc['LATITUDE'][k] or not columns_loc['LONGITUDE'][k]):
                        print('no latitude/longitude for this event: ', flood_jj)
                    else:
                        index2 = index2+1
                        sumlat = sumlat + float(columns_loc['LATITUDE'][k])
                        sumlon = sumlon + float(columns_loc['LONGITUDE'][k])
                if (index2 <= 0):
                    print('index2 <= 0 ')
                else:
                    lat_eventx = sumlat/index2
                    lon_eventx = sumlon/index2
                    if (lat_eventx >= lat_min and lat_eventx <= lat_max and lon_eventx >= lon_min and lon_eventx <= lon_max):
                        episode_flood_lat_jul[ii,jj] = lat_eventx
                        episode_flood_lon_jul[ii,jj] = lon_eventx
                    
                        #-----find flood type-----
                        index3     = [j for j in range(len(columns['EVENT_ID'])) if columns['EVENT_ID'][j] == flood_jj]
            #             print('len(index3), index3:', len(index3), index3)
                        if (columns['EVENT_TYPE'][index3[0]] == 'Flood'):
                            episode_flood_type_jul[ii,jj] = 1
                        elif (columns['EVENT_TYPE'][index3[0]] == 'Flash Flood'):
                            episode_flood_type_jul[ii,jj] = 2

                        #-----find time information-----
                        begin_time = columns['BEGIN_DATE_TIME'][index3[0]]
                        end_time   = columns['END_DATE_TIME'][index3[0]]
                        if (len(columns['CZ_TIMEZONE'][index3[0]]) < 4):
                            time_zone_int = find_hour_offset(columns['CZ_TIMEZONE'][index3[0]][0:3])
                        else:
                            time_zone_int = int(columns['CZ_TIMEZONE'][index3[0]][3:5])
                        if (time_zone_int < 0):
                            gettz          = Zone(time_zone_int,False,columns['CZ_TIMEZONE'][index3[0]][0:3])
                            time_start     = datetime.strptime(columns['BEGIN_DATE_TIME'][index3[0]],'%d-%b-%y %H:%M:%S').replace(tzinfo=gettz)
                            time_end       = datetime.strptime(columns['END_DATE_TIME'][index3[0]],'%d-%b-%y %H:%M:%S').replace(tzinfo=gettz)
                            time_start_utc = get_hour_utc(time_start)
                            time_end_utc   = get_hour_utc(time_end)
                            episode_flood_time1_jul[ii,jj] = int(time_start_utc)
                            episode_flood_time2_jul[ii,jj] = int(time_end_utc)
                        else:
                            print('time_zone_int > 0: ', columns['CZ_TIMEZONE'][index3[0]][0:3], time_zone_int)

    #-----output matrix variables-----
    outfile1 = path1 + 'StormEvent_episodes_jul_'+str(iyear)+'.csv'
    outfile2 = path1 + 'StormEvent_episodes_floods_jul_'+str(iyear)+'.csv'
    outfile3 = path1 + 'StormEvent_episodes_floods_lat_jul_'+str(iyear)+'.csv'
    outfile4 = path1 + 'StormEvent_episodes_floods_lon_jul_'+str(iyear)+'.csv'
    outfile5 = path1 + 'StormEvent_episodes_floods_time1_jul_'+str(iyear)+'.csv'
    outfile6 = path1 + 'StormEvent_episodes_floods_time2_jul_'+str(iyear)+'.csv'
    outfile7 = path1 + 'StormEvent_episodes_floods_type_jul_'+str(iyear)+'.csv'
    np.savetxt(outfile1, episode_matrix_jul, delimiter=",")
    np.savetxt(outfile2, episode_flood_matrix_jul, delimiter=",")
    np.savetxt(outfile3, episode_flood_lat_jul, delimiter=",")
    np.savetxt(outfile4, episode_flood_lon_jul, delimiter=",")
    np.savetxt(outfile5, episode_flood_time1_jul, delimiter=",")
    np.savetxt(outfile6, episode_flood_time2_jul, delimiter=",")
    np.savetxt(outfile7, episode_flood_type_jul, delimiter=",")
    

    #-----repeat for august-----
    flood_size = 0
    for ii in range(len(episode_aug)):
        if (flood_size < len(episode_flood_aug[ii])):
            flood_size = len(episode_flood_aug[ii])
    episode_matrix_aug      = np.zeros(len(episode_aug))
    episode_flood_matrix_aug= np.zeros((len(episode_aug), flood_size))
    episode_flood_lat_aug   = np.zeros((len(episode_aug), flood_size))
    episode_flood_lon_aug   = np.zeros((len(episode_aug), flood_size))
    episode_flood_time1_aug = np.zeros((len(episode_aug), flood_size))
    episode_flood_time2_aug = np.zeros((len(episode_aug), flood_size))
    episode_flood_type_aug  = np.zeros((len(episode_aug), flood_size))
    for ii in range(len(episode_aug)):
        episode_ii = episode_aug[ii]
        episode_matrix_aug[ii] = episode_ii
        for jj in range(len(episode_flood_aug[ii])):
            flood_jj   = episode_flood_aug[ii][jj]
            episode_flood_matrix_aug[ii,jj] = flood_jj
            #-----find lat and lon info-----
            index1     = [j for j in range(len(columns_loc['EVENT_ID'])) if columns_loc['EVENT_ID'][j] == flood_jj]
            if not index1:
                print("EVENT NOT FOUND.")
            else:
                # get an average if multiple locations are found
                sumlat = 0.0
                sumlon = 0.0
                index2 = 0.0
                j_ind  = -1
                i_ind  = -1
                for k in index1:
                    if (not columns_loc['LATITUDE'][k] or not columns_loc['LONGITUDE'][k]):
                        print('no latitude/longitude for this event: ', flood_jj)
                    else:
                        index2 = index2+1
                        sumlat = sumlat + float(columns_loc['LATITUDE'][k])
                        sumlon = sumlon + float(columns_loc['LONGITUDE'][k])
                if (index2 <= 0):
                    print('index2 <= 0 ')
                else:
                    lat_eventx = sumlat/index2
                    lon_eventx = sumlon/index2
                    if (lat_eventx >= lat_min and lat_eventx <= lat_max and lon_eventx >= lon_min and lon_eventx <= lon_max):
                        episode_flood_lat_aug[ii,jj] = lat_eventx
                        episode_flood_lon_aug[ii,jj] = lon_eventx
                    
                        #-----find flood type-----
                        index3     = [j for j in range(len(columns['EVENT_ID'])) if columns['EVENT_ID'][j] == flood_jj]
            #             print('len(index3), index3:', len(index3), index3)
                        if (columns['EVENT_TYPE'][index3[0]] == 'Flood'):
                            episode_flood_type_aug[ii,jj] = 1
                        elif (columns['EVENT_TYPE'][index3[0]] == 'Flash Flood'):
                            episode_flood_type_aug[ii,jj] = 2

                        #-----find time information-----
                        begin_time = columns['BEGIN_DATE_TIME'][index3[0]]
                        end_time   = columns['END_DATE_TIME'][index3[0]]
                        if (len(columns['CZ_TIMEZONE'][index3[0]]) < 4):
                            time_zone_int = find_hour_offset(columns['CZ_TIMEZONE'][index3[0]][0:3])
                        else:
                            time_zone_int = int(columns['CZ_TIMEZONE'][index3[0]][3:5])
                        if (time_zone_int < 0):
                            gettz          = Zone(time_zone_int,False,columns['CZ_TIMEZONE'][index3[0]][0:3])
                            time_start     = datetime.strptime(columns['BEGIN_DATE_TIME'][index3[0]],'%d-%b-%y %H:%M:%S').replace(tzinfo=gettz)
                            time_end       = datetime.strptime(columns['END_DATE_TIME'][index3[0]],'%d-%b-%y %H:%M:%S').replace(tzinfo=gettz)
                            time_start_utc = get_hour_utc(time_start)
                            time_end_utc   = get_hour_utc(time_end)
                            episode_flood_time1_aug[ii,jj] = int(time_start_utc)
                            episode_flood_time2_aug[ii,jj] = int(time_end_utc)
                        else:
                            print('time_zone_int > 0: ', columns['CZ_TIMEZONE'][index3[0]][0:3], time_zone_int)

    #-----output matrix variables-----
    outfile1 = path1 + 'StormEvent_episodes_aug_'+str(iyear)+'.csv'
    outfile2 = path1 + 'StormEvent_episodes_floods_aug_'+str(iyear)+'.csv'
    outfile3 = path1 + 'StormEvent_episodes_floods_lat_aug_'+str(iyear)+'.csv'
    outfile4 = path1 + 'StormEvent_episodes_floods_lon_aug_'+str(iyear)+'.csv'
    outfile5 = path1 + 'StormEvent_episodes_floods_time1_aug_'+str(iyear)+'.csv'
    outfile6 = path1 + 'StormEvent_episodes_floods_time2_aug_'+str(iyear)+'.csv'
    outfile7 = path1 + 'StormEvent_episodes_floods_type_aug_'+str(iyear)+'.csv'
    np.savetxt(outfile1, episode_matrix_aug, delimiter=",")
    np.savetxt(outfile2, episode_flood_matrix_aug, delimiter=",")
    np.savetxt(outfile3, episode_flood_lat_aug, delimiter=",")
    np.savetxt(outfile4, episode_flood_lon_aug, delimiter=",")
    np.savetxt(outfile5, episode_flood_time1_aug, delimiter=",")
    np.savetxt(outfile6, episode_flood_time2_aug, delimiter=",")
    np.savetxt(outfile7, episode_flood_type_aug, delimiter=",")
    


# #### Refine episode information

# In[22]:


#-----loop through each year and each month----

month_str = ['apr','may','jun','jul','aug']

for iyear in range(year1, year2):
    for imonth in range(5):
        file1 = path1 + 'StormEvent_episodes_'             +month_str[imonth]+'_'+str(iyear)+'.csv'
        file2 = path1 + 'StormEvent_episodes_floods_'      +month_str[imonth]+'_'+str(iyear)+'.csv'
        file3 = path1 + 'StormEvent_episodes_floods_lat_'  +month_str[imonth]+'_'+str(iyear)+'.csv'
        file4 = path1 + 'StormEvent_episodes_floods_lon_'  +month_str[imonth]+'_'+str(iyear)+'.csv'
        file5 = path1 + 'StormEvent_episodes_floods_time1_'+month_str[imonth]+'_'+str(iyear)+'.csv'
        file6 = path1 + 'StormEvent_episodes_floods_time2_'+month_str[imonth]+'_'+str(iyear)+'.csv'
        file7 = path1 + 'StormEvent_episodes_floods_type_' +month_str[imonth]+'_'+str(iyear)+'.csv'
        
        episode_ids         = np.genfromtxt(file1, delimiter=',')
        episode_flood_ids   = np.genfromtxt(file2, delimiter=',')
        episode_flood_lat   = np.genfromtxt(file3, delimiter=',')
        episode_flood_lon   = np.genfromtxt(file4, delimiter=',')
        episode_flood_time1 = np.genfromtxt(file5, delimiter=',')
        episode_flood_time2 = np.genfromtxt(file6, delimiter=',')
        episode_flood_type  = np.genfromtxt(file7, delimiter=',')
        
        episode_info        = np.zeros((episode_ids.shape[0],11))
        count1              = -1
        for ii in range(episode_ids.shape[0]):
            if (np.count_nonzero(episode_flood_lat[ii,:])>0):
                count1 = count1+1
                episode_info[count1,0] = episode_ids[ii]
                episode_info[count1,1] = np.count_nonzero(episode_flood_lat[ii,:])
                episode_info[count1,2] = np.count_nonzero(episode_flood_type[ii,:] == 1)   #flood
                episode_info[count1,3] = np.count_nonzero(episode_flood_type[ii,:] == 2)   #flash flood
                episode_info[count1,4] = np.ma.masked_equal(episode_flood_lat[ii,:],0).mean()
                episode_info[count1,5] = np.ma.masked_equal(episode_flood_lon[ii,:],0).mean()
                if (np.count_nonzero(episode_flood_lat[ii,:])>2):
                    episode_info[count1,10] = 1     #flag
                    lat_list0 = episode_flood_lat[ii,:][episode_flood_lat[ii,:]!=0]
                    lon_list0 = episode_flood_lon[ii,:][episode_flood_lon[ii,:]!=0]
                    lat_min  = lat_list.min()
                    lat_max  = lat_list.max()
                    lat_mean = episode_info[count1,4]
                    lon_mean = episode_info[count1,5]
                    lat_list,lon_list = sortVertices(lat_list0,lon_list0)
                    pa   = Proj("+proj=aea +lat_1="+str(lat_min)+" +lat_2="+str(lat_max)+" +lat_0="+str(lat_mean)+" +lon_0="+str(lon_mean))
                    x, y = pa(lon_list, lat_list)
                    cop = {"type": "Polygon", "coordinates": [zip(x, y)]}
                    episode_info[count1,6] = shape(cop).area/(1.e+6)
                episode_info[count1,7] = np.ma.masked_equal(episode_flood_time1[ii,:],0).min()
                episode_info[count1,8] = np.ma.masked_equal(episode_flood_time2[ii,:],0).max()
                episode_info[count1,9] = count_hours(episode_info[count1,7],episode_info[count1,8])
                
        #-----output matrix-----
        outfile1 = path1 + 'StormEvent_episodes_info_' +month_str[imonth]+'_'+str(iyear)+'.csv'
        np.savetxt(outfile1, episode_info[0:count1+1,:], delimiter=",")
        print('month, year:', month_str[imonth], iyear)
                    
    
    


# In[34]:


month_str[0]


# In[21]:


lat_list0 = np.asarray([30,40,30,40,35])
lon_list0 = np.asarray([-100,-100,-110,-110,-105])

lat_list,lon_list = sortVertices(lat_list0,lon_list0)
lat_min = min(lat_list)
lat_max = max(lat_list)
lat_mean = lat_list.mean()
lon_mean = lon_list.mean()
pa   = Proj("+proj=aea +lat_1="+str(lat_min)+" +lat_2="+str(lat_max)+" +lat_0="+str(lat_mean)+" +lon_0="+str(lon_mean))
x, y = pa(lon_list, lat_list)
cop  = {"type": "Polygon", "coordinates": [zip(x, y)]}
out1 = shape(cop).area/(1.e+6)
print(out1)


# In[13]:





# In[16]:


sortVertices(lat_list, lon_list)


# In[ ]:




