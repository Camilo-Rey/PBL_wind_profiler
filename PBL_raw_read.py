#!/usr/bin/env python
# coding: utf-8

# # Read, and process raw data of NOAA wind profiler
# ## By Camilo Rey and Vinnie Ribeiro
# ### Dec 27, 2019
# #### This code  Selects and process the SNR values for calculation of PBL code in the next code

########## First, Select the directory where the data was downloaded. Do not include the year in the directory ################
########## Second, adjust angle of oblique channels and offset according to the site #############################################

# Import libraries

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import pytz


# Parameters input

site='twi'
year=2018
yr=str(year)

ang=66.4 # inclination angle from horizon of non-vertical channels. If alredy corrected, ang=90
offset=-8 # offset from UTC

## Where is the data?

currdir=os.getcwd() # or other directory where data is located 
maindir=os.path.join(currdir, yr)


## Fine Resolution data example
#X1= pd.read_csv(os.path.join(maindir, '300\\tci17300.04w'),sep='\s+',skiprows=10,nrows=44)
#X1.head(5)
#
## Coarse Resolution data example
#X2= pd.read_csv(os.path.join(maindir, '300\\tci17300.04w'),sep='\s+',skiprows=66,nrows=62)
#X2.head(5)


## Preallocate

res=1 # 1 for fine, 2 for coarse
# if res==1:
#     ng=45
#     skp=10
# if res==2:
#     ng=62
#     skp=66
    

Ndays=365

h=np.empty((Ndays*24,ng),dtype=float);h[:]=np.nan
windspeed=np.empty((Ndays*24,ng),dtype=float);windspeed[:]=np.nan


snr1a=np.empty((Ndays*24,ng),dtype=float);snr1a[:]=np.nan
snr2a=np.empty((Ndays*24,ng),dtype=float);snr2a[:]=np.nan
snr3a=np.empty((Ndays*24,ng),dtype=float);snr3a[:]=np.nan

snr1s=np.empty((Ndays*24,ng),dtype=float);snr1s[:]=np.nan
snr2s=np.empty((Ndays*24,ng),dtype=float);snr2s[:]=np.nan
snr3s=np.empty((Ndays*24,ng),dtype=float);snr3s[:]=np.nan

snr2c=np.empty((Ndays*24,ng),dtype=float);snr2c[:]=np.nan
snr3c=np.empty((Ndays*24,ng),dtype=float);snr3c[:]=np.nan   

## Create time vector

# days in a year
days = []
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
        
# Populate time        
from datetime import datetime,timedelta

time=[]
date_0 = datetime(2018,1,1,0,0,tzinfo=pytz.timezone('US/Pacific'))
for day in days:
    date_1 = date_0+timedelta(int(day)-1)
    
    for hr in hrs:
        date_2 = date_1 + timedelta(0,3600*int(hr))
        time.append(date_2)

## Populate arrays



def get_ang_ng(filepath):
    # Function to obtain angle from data
    # Note: This function assuems a very specific
    # format in the files 

    with open(filepath) as file:
        lengs = []
        for i,row in enumerate(file):
            lengs.append(len(row))
            if i==9: # Getting 10th row
                row10 = list(row.split(" "))

    row10_clean = []
    for item in row10:
        if item != '':
            row10_clean.append(item)

    ang = float(row10_clean[3])


    ng_1 = 0
    while lengs[10+ng_1]==max(lengs) or ng_1>100:
        ng_1+=1 

    if res==1:
        ng = ng_1-1
    else:
        ng = 0
        while lengs[20+ng_1+ng]==max(lengs) or ng>100:
            ng+=1
        ng -= 1

    return ang, ng


d=0
for fileD in days:
    doy=int(fileD)
    direc=os.path.join(maindir, fileD)
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

            if d == 0 and c == 0:
                ang,ng = get_ang_ng(os.path.join(direc, fileH))
                # print(ang, ng, res)
            
            try:
                tabday = pd.read_csv(os.path.join(direc, fileH),sep='\s+',skiprows=skp,nrows=ng)
                h[d*24+c,:]=tabday['HT']
                h2=h[d*24+c,:]*np.sin(ang*np.pi/180);#h2=h2.reshape(-1,1)# Corrected height for the oblique channels
                windspeed[d*24+c,:]=tabday['SPD'].to_numpy(dtype='float'); windspeed[windspeed==999999]=np.nan                     
                s1o=tabday['SNR'].to_numpy(dtype='float');s1o[s1o==999999]=np.nan
                s2o=tabday['SNR.1'].to_numpy(dtype='float');s2o[s2o==999999]=np.nan
                s3o=tabday['SNR.2'].to_numpy(dtype='float');s3o[s3o==999999]=np.nan
                
                # Range-correction
                s1=s1o + 20*np.log10(tabday['HT']*1000)
                s2=s2o + 20*np.log10(tabday['HT']*1000)
                s3=s3o + 20*np.log10(tabday['HT']*1000)
                
                # Smoothing and heigth correcting:
                if sum(~np.isnan(s1))>10:
                    ss1=signal.savgol_filter(s1[~np.isnan(s1)],11,9)
                    snr1s[d*24+c,~np.isnan(s1)]=ss1                        
                if sum(~np.isnan(s2))>10:
                    ss2=np.interp(tabday['HT'],h2,s2)
                    snr2c[d*24+c,:]=ss2
                    snr2s[d*24+c,~np.isnan(ss2)]=signal.savgol_filter(ss2[~np.isnan(ss2)],11,9)
                if sum(~np.isnan(s3))>10:
                    ss3=np.interp(tabday['HT'],h2,s3)
                    snr3c[d*24+c,:]=ss3
                    snr3s[d*24+c,~np.isnan(ss3)]=signal.savgol_filter(ss3[~np.isnan(ss3)],11,9)
            except: 
                h[d*24+c,:]=np.nan                
                s1=np.empty((1,ng),dtype=float);s1[:]=np.nan
                s2=np.empty((1,ng),dtype=float);s2[:]=np.nan
                s3=np.empty((1,ng),dtype=float);s3[:]=np.nan
                    
            # Raw series    
            snr1a[d*24+c,:]=s1
            snr2a[d*24+c,:]=s2
            snr3a[d*24+c,:]=s3                 

  
            c+=1
        d+=1

     

# Sanity check: Plotting the wind speed at the minimum height along time
plt.figure()
plt.plot(time,windspeed[:,5])
plt.xlabel('time')
plt.ylabel('wind_speed (m/s)')
plt.show()

# Sanity check: Plotting the smoothed time series
plt.figure()
plt.plot(snr1s[4380,:],tabday['HT'],'.')
plt.plot(snr1s[4380,:],tabday['HT'])
plt.xlabel('SNR (dB)')
plt.ylabel('heigth(m)')
plt.show()
h=tabday['HT']
## Offset the time series to local time

offs=-offset

snr1=np.empty((Ndays*24,ng),dtype=float);snr1[:]=np.nan
snr2=np.empty((Ndays*24,ng),dtype=float);snr2[:]=np.nan
snr3=np.empty((Ndays*24,ng),dtype=float);snr3[:]=np.nan
ws=np.empty((Ndays*24,ng),dtype=float);ws[:]=np.nan

snr1[0:-offs-1]=snr1s[offs:-1,:]
snr2[0:-offs-1]=snr2s[offs:-1,:]
snr3[0:-offs-1]=snr3s[offs:-1,:]

np.savez(f'snr_coarse_new_{site}{year}',snr1, snr2, snr3,h,time,)
np.save(f'time_{site}{year}',time)
