#!/usr/bin/env python
# coding: utf-8

# # Read, and process raw data of NOAA wind profiler
# ## By Camilo Rey and Vinnie Ribeiro
# ### Dec 27, 2019
# #### This code  Selects and process the SNR values for calculation of PBL code in the next code


# Import libraries

import pandas as pd
import os
import numpy as np
import ftplib
import io
import time


# Parameters input

year=2017
yr=str(year)

ang=66.4 # inclination angle from horizon of non-vertical channels. If alredy corrected, ang=90
offset=-8 # offset from UTC

## Where is the data?

currdir=os.getcwd() # or other directory where data is located 
maindir=os.path.join(currdir, yr)


# Fine Resolution data example
X1= pd.read_csv(os.path.join(maindir, '300\\tci17300.04w'),sep='\s+',skiprows=10,nrows=44)
X1.head(5)

# Coarse Resolution data example
X2= pd.read_csv(os.path.join(maindir, '300\\tci17300.04w'),sep='\s+',skiprows=66)
X2.head(5)


## Preallocate

ALL_fine=np.empty((44*24*365,16),dtype=float);ALL_fine[:]=np.nan
ALL_coarse=np.empty((62*24*365,16),dtype=float);ALL_coarse[:]=np.nan

hrall_fine=[]
doyall=[]
hrall_coarse=[]
doyall_coarse=[]

d=0
days = []

# days in a year
for i in  np.arange(1,366):
    if len(str(i))==1:
        days.append('00'+str(i))
    elif len(str(i))==2:
        days.append('0'+str(i))
    else:
        days.append(str(i))

# hours in a day
hrs = []
for i in  np.arange(24):
    if len(str(i))==1:
        hrs.append('0'+str(i))
    else:
        hrs.append(str(i))        

## Populate arrays

for fileD in days:
        print(fileD)
        doy=int(fileD)
        direc=os.path.join(maindir, fileD)
        # Pre-allocate 

        day=np.empty((44*24,16),dtype=float)
        dayc=np.empty((62*24,16),dtype=float)

        c=0            
        # Iterate through hours in a day

        try:
            fname = os.listdir(direc)[0]
        except:
            fname = None
            
        if fname is not None:
            print('working on file', fname)
            for hr in hrs:
                fileH = fname[0:9]+str(hr)+'w'
                
                for i in range(44):
                    hrall_fine.append(int(hr))
                    doyall.append(doy)                 

                for i in range(62):
                    hrall_coarse.append(int(hr))
                    doyall_coarse.append(doy)

                try:
                    # Fine Resolution dataset
                    day[c*44:c*44+44]= pd.read_csv(os.path.join(direc, fileH),sep='\s+',skiprows=10,nrows=44)
                    dayc[c*62:c*62+62]= pd.read_csv(os.path.join(direc, fileH),sep='\s+',skiprows=66,nrows=62)
                
                except:
                    day[c*44:c*44+44] = None
                    dayc[c*62:c*62+62]= None
    
                c+=1

        
        ALL_fine[d*1056:d*1056+1056]=day
        ALL_coarse[d*1488:d*1488+1488]=dayc
        d+=1


print(day,day.shape)  
print(ALL_fine,ALL_fine.shape)
len(doyall)


# Define date and time variables (not sure this is the best way to do it)
# Note: The calculations for time_fine and time_coarse could have been 
# performed in the same loop as ALL_fine and ALL_coarse, they are separated
# for now just to make it easier to debug.

from datetime import datetime,timedelta

time_fine=[]

date_0 = datetime(year,1,1,0,0)


for day in days:
    date_1 = date_0+timedelta(int(day)-1)
    
    for hr in hrs:
        date_2 = date_1 + timedelta(0,3600*int(hr))
        
        for imin in range(44):
            date = date_2 + timedelta(0,60*imin*(60/44))
            time_fine.append(date)
#            print(date.isoformat()) # To check values as generated
        

time_coarse=[]

for day in days:
    date_1 = date_0+timedelta(int(day)-1)
    
    for hr in hrs:
        date_2 = date_1 + timedelta(0,3600*int(hr))
        
        for imin in range(62):
            date = date_2 + timedelta(0,60*imin*(60/62))
            time_coarse.append(date)
#            print(date.isoformat()) # To check values as generated
        

# Note: This part is commented out for testing purposes
#import matplotlib
#import matplotlib.pyplot as plt
#
#timenum=matplotlib.dates.date2num(timeall)
#timenum[1:10]
#len(doyall)
#fig, ax = plt.subplots()
#ax.plot(timenum,doyall)
#
#
#import matplotlib.dates as mdates
#myFmt = mdates.DateFormatter('%m')
#ax.xaxis.set_major_formatter(myFmt)
#
#plt.ylabel('DOY')
#plt.xlabel('month')
#
#plt.show()
#
#
#
## Extracting Signal-to-Noise ratio data (SNR) and others, and correcting heigths
#
#snr1a=ALL_fine[:,11];snr1a[snr1a==999999]=None
#snr2a=ALL_fine[:,12];snr2a[snr2a==999999]=None
#snr3a=ALL_fine[:,13];snr3a[snr3a==999999]=None
#
#h=ALL_fine[:,1];h[h==999999]=None
#
#h2=h*np.sin(ang*np.pi/180);# Corrected height for the oblique channels
#snr2c=np.interp(h2,snr2a,h);# interpolate the corrected values to the height of the vertical
#snr3c=np.interp(h2,snr3a,h);# interpolate the corrected values to the height of the vertical
#
#
#
#
## Offset the time series to local time
#
#ltt=len(doyall)
#offs=-offset
#snr=np.concatenate((snr1a.reshape(-1,1),snr3c.reshape(-1,1)),axis=1)
#snr=np.concatenate((snr,snr3c.reshape(-1,1)),axis=1)
#snr.shape
##snr1=np.empty((len(snr1a),1),dtype=float);
##snr1[-1]
## snr[offs:-1,1]=snr[1:ltt-offs] #offset snr is in UTC

