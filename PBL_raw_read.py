#!/usr/bin/env python
# coding: utf-8

# # Download, read, and process raw data of NOAA wind profiler
# ## By Camilo Rey and Vinnie Ribeiro
# ### Dec 27, 2019
# #### This code 1) downloads a selected subset of the raw data of the NOAA wind profiler from the NOAA ftp server and stores it in the local machine. 2) Selects and process the SNR values for calculation of PBL code in the next code

# In[1]:


# Import libraries

import pandas as pd
import os
import numpy as np
import ftplib
import io
import time

# In[2]:


# Parameters input

year=2017
yr=str(year)

ndays=365
ang=66.4 # inclination angle from horizon of non-vertical channels. If alredy corrected, ang=90
offset=-8 # offset from UTC


# In[3]:

# Dowload data from NOAA and store it in current working directory

ftp = ftplib.FTP("ftp1.esrl.noaa.gov")
ftp.login()

base = '/psd2/data/realtime//Radar915/WwWind/tci/'


def download(folder):
    
    files = os.listdir(folder[len(base)::])
    for file in ftp.nlst(folder):
        if file not in files:

            r = io.BytesIO()
            ftp.retrbinary('RETR ' + file , r.write)
            data = r.getvalue()

            path = os.path.join(os.getcwd(),folder[len(base)::])

            file_name = file[len(folder)+1::]
            with open(os.path.join(path,file_name),'wb') as f:
                f.write(data)

            r.close()
        else:
            pass


t_init = time.time()

path = os.path.join(base,str(year))

for path0 in ftp.nlst(path):
    try:
        os.makedirs(path0[len(base)::])
    except FileExistsError:
        pass
#     print(os.listdir(path0[len(base)::]))
#     print(path0)
    download(path0)
    currdir=os.getcwd()

t_final = time.time()
print(f'Time without skipping already downloaded files (2017): {t_final-t_init}')

maindir=os.path.join(currdir, yr)
ndays=len(os.listdir(maindir))

# In[5]:

# Work on the examples later

## Fine Resolution data example
#X1= pd.read_csv(os.path.join(maindir, ),sep='\s+',skiprows=10,nrows=44)
#X1.head(5)


# In[6]:


## Coarse Resolution data example
#X1= pd.read_csv(r'D:\PBL\Raw\2018\003\tci18003.00w',sep='\s+',skiprows=66)
#X1.head(5)


# In[ ]:

# New version!!!

ALL_fine=np.empty((44*24*365,16),dtype=float);ALL_fine[:]=np.nan
ALL_coarse=np.empty((62*24*365,16),dtype=float);ALL_coarse[:]=np.nan

hrall_fine=[]
doyall=[]
hrall_coarse=[]
doyall_coarse=[]

d=0
days = []

for i in  np.arange(1,366):
    if len(str(i))==1:
        days.append('00'+str(i))
    elif len(str(i))==2:
        days.append('0'+str(i))
    else:
        days.append(str(i))

hrs = []
for i in  np.arange(24):
    if len(str(i))==1:
        hrs.append('0'+str(i))
    else:
        hrs.append(str(i))        

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



# In[114]:


# Define date and time variables (not sure this is the best way to do it)
import datetime as dt

time_fine=[]
yearF=?
monthF=?
dayF=?
hourF=?

for i in range(44*24*365):    
    t1=dt.datetime(yearF[i],monthF[i],dayF[i],hourF[i])
    time_fine.append(t1)

    
time_coarse=[]
yearG=?
monthG=?
dayG=?
hourG=?

for i in range(44*24*365):    
    t2=dt.datetime(yearG[i],monthG[i],dayG[i],hourG[i])
    time_coarse.append(t2)
    

# In[ ]:





# In[116]:


import matplotlib
import matplotlib.pyplot as plt
timenum=matplotlib.dates.date2num(timeall)
timenum[1:10]
len(doyall)
fig, ax = plt.subplots()
ax.plot(timenum,doyall)


import matplotlib.dates as mdates
myFmt = mdates.DateFormatter('%m')
ax.xaxis.set_major_formatter(myFmt)

plt.ylabel('DOY')
plt.xlabel('month')

plt.show()


# In[ ]:


# Extracting Signal-to-Noise ratio data (SNR) and others, and correcting heigths

snr1a=ALL_fine[:,11];snr1a[snr1a==999999]=None
snr2a=ALL_fine[:,12];snr2a[snr2a==999999]=None
snr3a=ALL_fine[:,13];snr3a[snr3a==999999]=None

h=ALL_fine[:,1];h[h==999999]=None

h2=h*np.sin(ang*np.pi/180);# Corrected height for the oblique channels
snr2c=np.interp(h2,snr2a,h);# interpolate the corrected values to the height of the vertical
snr3c=np.interp(h2,snr3a,h);# interpolate the corrected values to the height of the vertical


# In[118]:


# Offset the time series to local time

ltt=len(doyall)
offs=-offset
snr=np.concatenate((snr1a.reshape(-1,1),snr3c.reshape(-1,1)),axis=1)
snr=np.concatenate((snr,snr3c.reshape(-1,1)),axis=1)
snr.shape
#snr1=np.empty((len(snr1a),1),dtype=float);
#snr1[-1]
# snr[offs:-1,1]=snr[1:ltt-offs] #offset snr is in UTC
