# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 19:10:40 2020

@author: 16146
"""
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pytz
from datetime import datetime,timedelta

site='twi'
year=2018
gg=np.load('snr_coarse_new_twi2018.npz', allow_pickle=True)
gg.files

snr1=gg['arr_0']
snr2=gg['arr_1']
snr3=gg['arr_2']
h=gg['arr_3']
plottime=gg['arr_4']


##=======================================================
### From this point is all Matlab code that needs to be translated
#
## First I need to create an array with the day of year extracting it from plottime


# days go from 1 to 365
doy = np.array([date.timetuple().tm_yday for date in plottime])

# extract integer hour for all time series (0:23)
hours = [date.hour for date in plottime]

#daysun3=nan(length(doy),1);
daysun3 = np.array([np.nan for i in doy])

# shift the time by 5 hour
#daysun3[0:5] = doy[-5:]
daysun3[5:] = doy[0:-5]




## Second, we need an array of sunrise and sunset times based on location of instrument
#
## These are the coordinates of the place to determine sunset and sunrise times

LLA = [-121.64125, 38.10275, -10]
longitude = LLA[0] # degrees - longitude of tower location
latitude  =  LLA[1] # degrees - latitude of tower location
altitude  =  LLA[2] # m - altitude of tower location


from astral import LocationInfo

city = LocationInfo("Sacramento", "California", "US", LLA[1], LLA[0])

# =============================================================================
# site = LocationInfo((
#         'site',
#         'US',
#         latitude,
#         longitude,
#         'US/Pacific',
#         altitude
#         ))
# 
# =============================================================================


from astral.sun import sun

daynight = []
for time in plottime:
    
# =============================================================================
#     sr = site.sunrise(datetime(time.year,time.month,time.day))
#     ss = site.sunset(datetime(time.year,time.month,time.day))
# =============================================================================
    
    s = sun(city.observer, date=datetime(time.year,time.month,time.day))
    sr = s["sunrise"]
    ss = s["sunset"]

    if time>sr and time<ss:
        daynight.append(1)
    else:
        daynight.append(0)


daynight = np.array(daynight, dtype=bool)

# #=========================================================================
# ## Ready to loop through channels, then through days (in this case daysun3)

day_start = doy[0]
day_end = doy[-1]
Ndays = day_end - day_start + 1 
#Ndays=len(set(doy))

pbl_init=0.1 # km

allc = np.full([Ndays*24,3], np.nan)


for m,snrT in enumerate([snr1, snr2, snr3]):

    PBL = np.full(Ndays*24, np.nan)
    SUNSIX = np.full(Ndays*24, np.nan)
    
    for i in range(day_start,day_end+1):
    
        S1 = snrT[daysun3==i]
        DN = daynight[daysun3==i]         
        
        pbl24 = np.full(24, fill_value = np.nan)
        negSNR = np.full(24, fill_value = np.nan)
        
        offsunr = 3
        offsuns = 4
        
        sunrix = np.arange(len(DN))[DN==1][0] # this is the index
        sunsix = np.arange(len(DN))[DN==1][-1]+1 # this is the index
        ssix= np.zeros(24,dtype=int)
        ssix[sunrix+offsunr:sunsix+1-offsuns]= 1 ; # A vector of zeros and ones showing late afternoon       

        
        pbl = pbl_init
        pbl24[0] = pbl
        
        
        for j,s in enumerate(S1):             
            pp = np.sort(s)[::-1]
            ss = np.argsort(s)[::-1]
            
            s2 = ss[~np.isnan(pp)]
            p2 = pp[~np.isnan(pp)]
            
            if sum(~np.isnan(s[:20]))>10:
               
                #  from sunrise onwards
                Morn = 0.6 # maximum delta in the morning
                MinSNR = 0 # Minimum SNR to be considered as a peak
                if j >= (sunrix + offsunr) and j < (sunsix-offsuns) and i != day_end:
                    
                    if h[s2[0]] >= pbl and abs(h[s2[0]]-pbl) < Morn and p2[0] > MinSNR:
                        pbl = h[s2[0]] # Choose the maximum SNR within the window
                    
                    elif h[s2[1]] >= pbl and abs(h[s2[1]]-pbl) < Morn and p2[1] > MinSNR:
                        pbl = h[s2[1]] # Choose the maximum SNR within the window    
                    
                    elif h[s2[2]] >= pbl and abs(h[s2[2]]-pbl) < Morn and p2[2] > MinSNR:
                        pbl = h[s2[2]] # Choose the maximum SNR within the window      
                    
                    elif h[s2[3]] >= pbl and abs(h[s2[3]]-pbl) < Morn and p2[3] > MinSNR:
                        pbl = h[s2[3]] # Choose the maximum SNR within the window  
                    
                    elif h[s2[4]] >= pbl and abs(h[s2[4]]-pbl) < Morn and p2[4] > MinSNR:
                        pbl = h[s2[4]] # Choose the maximum SNR within the window
                    
                    elif h[s2[5]] >= pbl and abs(h[s2[5]]-pbl) < Morn and p2[5] > MinSNR:
                        pbl = h[s2[5]] # Choose the maximum SNR within the window 
                    
                    elif h[s2[6]] >= pbl and abs(h[s2[6]]-pbl) < Morn and p2[6] > MinSNR:
                        pbl = h[s2[6]] # Choose the maximum SNR within the window            
                        
                    negSNR[j] = p2[0] < MinSNR
                    
                    
                ## For mid-afternoon to sunset (decay)
                night = 0.95   # maximum delta in the night    
                if j >= sunsix-offsuns and j <= sunsix: # If it is nighttime (DN(j)==0) and after the afternoon(j>10)      
        
                    # Note: Is it correct that the index in h[s2[0]] doesnt
                    # change in the elifs? 
                    if abs(h[s2[0]]-pbl) < night and h[s2[0]] <= pbl:
                        pbl = h[s2[0]]  # Choose the maximum SNR within the window
                        
                    elif abs(h[s2[1]]-pbl) < night and h[s2[1]] <= pbl:
                        pbl = h[s2[1]]  # Else, choose the next maximum    
                        
                    elif abs(h[s2[2]]-pbl) < night and h[s2[2]] <= pbl:
                        pbl = h[s2[2]]  # Else, choose the next maximum
                        
                    elif abs(h[s2[3]]-pbl) < night and h[s2[3]] <= pbl:
                        pbl = h[s2[3]]  # Else, choose the next maximum
                        
                    elif abs(h[s2[4]]-pbl) < night and h[s2[4]] <= pbl:
                        pbl = h[s2[4]]  # Else, choose the next maximum
                        
                    elif abs(h[s2[5]]-pbl) < night and h[s2[5]] <= pbl:
                        pbl = h[s2[5]]  # Else, choose the next maximum
                        
                    elif abs(h[s2[6]]-pbl) < night and h[s2[6]] <= pbl:
                        pbl = h[s2[6]]  # Else, choose the next maximum
                    
                # For nighttime
                if j > sunsix:
                    pbl = np.nan 
                    
                # Allocate to daily file
                pbl24[j] = pbl 
                
            else:
                print('day '+str(i)+', hour '+str(j)+', channel '+str(m+1)+' not computed. '+str(sum(np.isnan(s[0:30])))+' nans in lower 30 points')    
                
                
        # Allocate to annual file
            
        if np.nansum(negSNR)>4:
            pbl24 = np.full(24, fill_value = np.nan)
                        
        if i == day_end:
            PBL[daysun3==i]=pbl24[:-5]
            SUNSIX[daysun3==i]=ssix[:-5]
        else:
            PBL[daysun3==i]=pbl24      
            SUNSIX[daysun3==i]=ssix
        
      
    allc[:,m]=PBL # Allocate to table with all channels
        
    

import copy
all_raw=copy.copy(allc)

## Filteing channels based on error

dm=np.nanmean(allc, axis=1)
err1=np.abs(allc[:,0]-dm)/dm
ixm1=err1>0.25
allc[ixm1,0]=np.nan

err2=np.abs(allc[:,1]-dm)/dm
ixm2=err2>0.25
allc[ixm2,1]=np.nan

err3=np.abs(allc[:,2]-dm)/dm
ixm3=err3>0.25
allc[ixm3,2]=np.nan

# Plot the 3 channels 
plt.figure(figsize=(10,8))
plt.plot(plottime, allc[:,0])
plt.plot(plottime, allc[:,1])
plt.plot(plottime, allc[:,2])
plt.ylabel('PBL height (Km)')
plt.legend({'ch_1', 'ch_2','ch_3'})
plt.title('Raw PBL height as determined by each channel')


# Creating a filter based on standard deviation
PBL_cam0 = np.nanmean(allc, axis=1) # Raw mean of PBL height from the three channels
PBL_SD = np.nanstd(allc, axis=1)
n = np.sum(~np.isnan(allc),axis=1)
SD_flag = np.bitwise_or(PBL_SD>0.2, n<2)
PBL_cam1=copy.copy(PBL_cam0) # First filtered PBL
PBL_cam1[SD_flag] = np.nan


# Filtering whole days
PBL_cam2 = copy.copy(PBL_cam1)
# If a day has high variation, the whole days is bad
for i in range(day_start,day_end+1):
    
    ix = doy==i    
    ix2 = np.bitwise_and(doy==i, daynight)
    ix3 = np.bitwise_and(doy==i, SUNSIX==1)
    if sum(np.isnan(PBL_cam1[ix3]))>=3 : # 3 or more nans during the day make the whole day bad
        PBL_cam2[ix]=np.nan; 
    if np.nanmax(PBL_cam1[ix2]) < 0.20: # if the maximum PBL for the day is less than the 150 m, the whole day is bad
        PBL_cam2[ix] = np.nan
        
# Interpolation to 30 and 15 min

hrs = np.arange(24) # hours
Dhour = np.arange(0,24,0.5) # desired hour 30 min
Dhour2 = np.arange(0,24,0.25) # desired hour 15 min

PBL_30min = []
PBL_15min = []
YEAR = []
daysun_30min = []
# yy = year 


for i in range(day_start,day_end+1):
    Hp = PBL_cam2[doy==i]
    
    h30min = np.interp(Dhour, hrs, Hp)
    PBL_30min.append(h30min)
    
    h15min = np.interp(Dhour2, hrs, Hp)
    PBL_15min.append(h15min)
#     YEAR=[YEAR,yy];

PBL_30min = np.array(PBL_30min).reshape(-1)
PBL_15min = np.array(PBL_15min).reshape(-1)

# plottime for 30 mins and one for 15 min and plot

date30min = []
date_0 = datetime(2018,1,1,0,0,tzinfo=pytz.timezone('US/Pacific'))
for day in list(set(doy)):
    date_1 = date_0+timedelta(int(day)-1)
    
    for i,t in enumerate(Dhour):
        date_2 = date_1 + timedelta(0,1800*i)
        date30min.append(date_2)


date15min = []
date_0 = datetime(2018,1,1,0,0,tzinfo=pytz.timezone('US/Pacific'))
for day in list(set(doy)):
    date_1 = date_0+timedelta(int(day)-1)
    
    for i,t in enumerate(Dhour2):
        date_2 = date_1 + timedelta(0,900*i)
        date15min.append(date_2)

plt.figure(figsize=(10,8))
plt.plot(date15min,PBL_15min)
plt.ylabel('PBL height (Km)')
plt.title('PBL height interpolated Half-hourly')

plt.figure(figsize=(10,8))
plt.plot(date30min,PBL_30min)
plt.ylabel('PBL height (Km)')
plt.title('PBL height interpolated to 15-min')

plt.show()
np.savez(f'PBL_heigth_{site}{year}',date30min, PBL_30min)

# Formatting output
res = np.empty((len(PBL_30min),2), dtype=object)
res[:,0] = PBL_30min
for i,date in enumerate(date30min):
    res[i,1] = date.isoformat(' ')
res = pd.DataFrame(res,columns=['PBL_30min', 'date30min'])
res.to_csv('Results') # Creating CSV output file.