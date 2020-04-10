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
        ssix= [np.nan for i in range(24)]
        ssix[sunsix-5:sunsix-1]= [1, 1, 1, 1] ; # A vector of zeros and ones showing late afternoon
        
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
            SUNSIX[daysun3==i]=ssix[:-5]
        else:
            PBL[daysun3==i]=pbl24      
            SUNSIX[daysun3==i]=ssix
        
      
    ALL[:,m]=PBL # Allocate to table with all channels
        
    


# Plot the 3 channels and their variability
plt.figure()
plt.plot(plottime, ALL[:,0])
plt.plot(plottime, ALL[:,1])
plt.plot(plottime, ALL[:,2])
plt.show()

PBL_cam0=nanmean(ALL,2);# Raw mean of PBL height from the three channels

# Creating a filter based on standard deviation
PBL_SD = np.nanstd(ALL, axis=0)
n=sum(~isnan(ALL),2);
SD_flag=PBL_SD>0.15 | n<2;
PBL_cam1=PBL_cam0;% First filtered PBL
PBL_cam1(SD_flag,:)=nan;

# Filtering whole days
PBL_cam2=PBL_cam1;  

# If a day has high variation, the whole days is bad
for i=1:365
    ix=doy_yr==i;    
    ix2= doy==i & daynight==1;
    ix3= doy==i & SUNSIX==1;
    if nansum(isnan(PBL_cam1(ix3)))>=3 : # 3 or more nans during the day make the whole day bad
        PBL_cam2(ix)=nan(nansum(ix),1);    
    if nanmax(PBL_cam1(ix2))<0.20 : # if the maximum PBL for the day is less than the 150 m, the whole day is bad
        PBL_cam2(ix)=nan(nansum(ix),1);
        
# Interpolation to 30 and 15 min

hr=(0:23)# huors
Dhour=(0:0.5:23.5)# desired hour 30 min
Dhour2=(0:0.25:23.75) # desired hour 15 min

PBL_30min_cam=[];PBL_15min_cam=[];
YEAR=[];
daysun_30min=[];
yy=year; 

for i=day_start:day_end:
    Hp=PBL_cam2(doy==i);
    h30min=interp1(hr,Hp,Dhour);
    PBL_30min_cam=[PBL_30min_cam;h30min];
    h15min=interp1(hr,Hp,Dhour2);
    PBL_15min_cam=[PBL_15min_cam;h15min];
    YEAR=[YEAR,yy];

# Now we need to create a new plottime for 30 mins and one for 15 min and plot

date30min=?
date15min=?    

figure;plot(date30min,[PBL_30min_cam]);title('Interpolated 30 min')
ylabel('PBL heigth (km)'); 

save([SaveDir 'PBL_30min'],'PBL_30min_cam','date30min','doy_res')

figure;plot(date15min,[PBL_15min_cam]);title('Interpolated 15 min')
ylabel('PBL heigth (km)');   

save([SaveDir 'PBL_15min'],'PBL_15min_cam','date15min','doy_res')    
