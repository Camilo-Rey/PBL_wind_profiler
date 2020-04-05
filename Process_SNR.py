# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 19:10:40 2020

@author: 16146
"""
import datetime
import numpy as np
import matplotlib.pyplot as plt

gg=np.load('snr_coarse_new.npz', allow_pickle=True)
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

SUNSIX = [np.nan for i in doy]


## Second, we need an array of sunrise and sunset times based on location of instrument
#
## These are the coordinates of the place to determine sunset and sunrise times

LLA = [-121.64125, 38.10275, -10]
longitude = LLA[0] # degrees - longitude of tower location
latitude  =  LLA[1] # degrees - latitude of tower location
altitude  =  LLA[2] # m - altitude of tower location


from astral import Location

site = Location((
        'site',
        'US',
        latitude,
        longitude,
        'US/Pacific',
        altitude
        ))


daynight = []
for time in plottime:
    
    sr = site.sunrise(datetime.datetime(time.year,time.month,time.day))
    ss = site.sunset(datetime.datetime(time.year,time.month,time.day))

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


ALL = np.full([Ndays*24,3], np.nan)


for m,snrT in enumerate([snr1, snr2, snr3]):

    PBL = np.full(Ndays*24, np.nan)
    
    for i in range(day_start,day_end+1):
    
        S1 = snrT[daysun3==i]
        DN = daynight[daysun3==i]   
        
        pbl24 = np.full(24, fill_value = np.nan)
        negSNR = np.full(24, fill_value = np.nan)
        
        sunrix = np.arange(len(DN))[DN==1][0]
        sunsix = np.arange(len(DN))[DN==1][-1]+1
        
        offsunr = 2
        offsuns = 2
        
        pbl = 0.15
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
                night = 0.75   # maximum delta in the night    
                if j >= sunsix-offsuns and j <= sunsix: # If it is nighttime (DN(j)==0) and after the afternoon(j>10)      
        
                    # Note: Is it correct that the index in h[s2[0]] doesnt
                    # change in the elifs? 
                    if abs(h[s2[0]]-pbl) < night and h[s2[0]] <= pbl:
                        pbl = h[s2[0]]  # Choose the maximum SNR within the window
                        
                    elif abs(h[s2[1]]-pbl) < night and h[s2[0]] <= pbl:
                        pbl = h[s2[1]]  # Else, choose the next maximum    
                        
                    elif abs(h[s2[2]]-pbl) < night and h[s2[0]] <= pbl:
                        pbl = h[s2[2]]  # Else, choose the next maximum
                        
                    elif abs(h[s2[3]]-pbl) < night and h[s2[0]] <= pbl:
                        pbl = h[s2[3]]  # Else, choose the next maximum
                        
                    elif abs(h[s2[4]]-pbl) < night and h[s2[0]] <= pbl:
                        pbl = h[s2[4]]  # Else, choose the next maximum
                        
                    elif abs(h[s2[5]]-pbl) < night and h[s2[0]] <= pbl:
                        pbl = h[s2[5]]  # Else, choose the next maximum
                        
                    elif abs(h[s2[6]]-pbl) < night and h[s2[0]] <= pbl:
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
        else:
            PBL[daysun3==i]=pbl24              
        
      
    ALL[:,m]=PBL # Allocate to table with all channels
        
    
PBL_SD = np.nanstd(ALL, axis=0)

# Plot the 3 channels and their variability
plt.figure()
plt.plot(plottime, ALL[:,0])
plt.plot(plottime, ALL[:,1])
plt.plot(plottime, ALL[:,2])
plt.show()