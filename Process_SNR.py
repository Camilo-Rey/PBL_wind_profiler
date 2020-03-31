# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 19:10:40 2020

@author: 16146
"""

import numpy as np
gg=np.load('snr_coarse_new.npz')
gg.files

snr1=gg['arr_0']
snr1=gg['arr_1']
snr1=gg['arr_2']
h=gg['arr_3']
plottime=gg['arr_4']# This is not working, I do not know why

plottime=np.load('timef.npy')# not working either...

#=======================================================
## From this point is all Matlab code that needs to be translated

# First I need to create an array with the day of year extracting it from plottime

doy=days(plottime,'dayofyear')# days go from 1 to 365
hours=hour(plottime)# extract integer hour for all time series (0:23)
daysun3=nan(length(doy),1);
daysun3(6:end)=doy(1:end-5);# shift the time by 5 hour
SUNSIX=nan(length(doy),1);

# Second, we need an array of sunrise and sunset times based on location of instrument

# These are the coordinates of the place to determine sunset and sunrise times

LLA=[-121.64125 38.10275 -10];
longitude = LLA(1); # degrees - longitude of tower location
latitude  =  LLA(2); # degrees - latitude of tower location
altitude  =  LLA(3); # m - altitude of tower location

UTC_offset=-8;
gtG = -(UTC_offset/24); # Time offset to get to Greenwhich

import datetime
from suntime import Sun, SunTimeException # Found this library but not sure if it works

sun = Sun(latitude, longitude)

# Get sunrise and sunset in UTC
sr = sun.get_sunrise_time()
ss = sun.get_sunset_time()

# After this the goal is to have an array of 0 and 1 for the length of the array (8760)
daynight= zeros(8760,1)
daynight(sr>hours>ss)=1

#=========================================================================
## Ready to loop through channels, then through days (in this case daysun3)

    day_start=doy(1);
    day_end=doy(end);
    Ndays=day_end-day_start+1;

    ALL=nan(Ndays*24,3);

for m=1:3 # loop through the channels
    
    if m==1:
        snrT=snr1
    if m==2:
        snrT=snr2
    if m==3:
        snrT=snr3   
    
    PBL=nan(Ndays*24,1);
    for i=day_start:day_end # loop though the number of days
    
        # Creating subsets for sunrise-to-sunrise days
        S1=snrT(daysun3==i,:);      
        DN=daynight(daysun3==i,:);    
        pbl24=nan(24,1);    
        negSNR=nan(24,1);
        
        ix44=find(DN==1);    
        sunrix=ix44(1);# sunrise index
        sunsix=ix44(end)+1;# sunset index
        ssix=zeros(24,1);ssix(sunsix-5:sunsix-1)=1;
            
        offsunr=2;# number of hours after sunrise to start pbl growth
        offsuns=2;# number of hours before sunset to stabilize pbl growth
        
        # Initial PBL (PBL at 5 am)
        pbl=0.15;
        pbl24(1)=pbl;    
        
        for j=1:length(DN): # Loop through the hours in a day        
            #Sort SNR values    
            s=S1(j,:);  
            [pp,ss]=sort(s,'descend');
            s2=ss(~isnan(pp));
            p2=pp(~isnan(pp));
    
            if sum(~isnan(s(1:20)))>10: # Run only if there are more than 10 data points in lower section
    
                #  from sunrise onwards
                Morn=0.6;# maximum delta in the morning
                MinSNR=0; # Minimum SNR to be considered as a peak
                if j>=sunrix + offsunr && j<sunsix-offsuns && i~=day_end:         
                    if h(s2(1))>=pbl && abs(h(s2(1))-pbl)<Morn && p2(1)>MinSNR:
                        pbl=h(s2(1));# Choose the maximum SNR within the window
                    elseif h(s2(2))>=pbl && abs(h(s2(2))-pbl)<Morn && p2(2)>MinSNR
                        pbl=h(s2(2));# Else, choose the next maximum      
                    elseif h(s2(3))>=pbl && abs(h(s2(3))-pbl)<Morn && p2(3)>MinSNR
                        pbl=h(s2(3));  # Else, choose the next maximum        
                    elseif h(s2(4))>=pbl && abs(h(s2(4))-pbl)<Morn && p2(4)>MinSNR
                        pbl=h(s2(4));# Else, choose the next maximum  
                    elseif h(s2(5))>=pbl && abs(h(s2(5))-pbl)<Morn && p2(5)>MinSNR
                        pbl=h(s2(5));  # Else, choose the next maximum  
                    elseif h(s2(6))>=pbl && abs(h(s2(6))-pbl)<Morn && p2(6)>MinSNR
                        pbl=h(s2(6));  # Else, choose the next maximum  
                    elseif h(s2(7))>=pbl && abs(h(s2(7))-pbl)<Morn && p2(7)>MinSNR
                        pbl=h(s2(7));  # Else, choose the next maximum              
                        
                    negSNR(j)=p2(1)<MinSNR;            
    
    
                ## For mid-afternoon to sunset (decay)
                night=0.75;    # maximum delta in the night    
                if j>=sunsix-offsuns && j<=sunsix # If it is nighttime (DN(j)==0) and after the afternoon(j>10)      
        
                    if abs(h(s2(1))-pbl)<night && h(s2(1))<=pbl
                        pbl=h(s2(1));# Choose the maximum SNR within the window
                    elseif abs(h(s2(2))-pbl)<night && h(s2(1))<=pbl
                        pbl=h(s2(2)); # Else, choose the next maximum    
                    elseif abs(h(s2(3))-pbl)<night && h(s2(1))<=pbl
                        pbl=h(s2(3));  # Else, choose the next maximum   
                    elseif abs(h(s2(4))-pbl)<night && h(s2(1))<=pbl
                        pbl=h(s2(4));# Else, choose the next maximum 
                    elseif abs(h(s2(5))-pbl)<night && h(s2(1))<=pbl
                        pbl=h(s2(5));  # Else, choose the next maximum 
                    elseif abs(h(s2(6))-pbl)<night && h(s2(1))<=pbl
                        pbl=h(s2(6));  # Else, choose the next maximum 
                    elseif abs(h(s2(7))-pbl)<night && h(s2(1))<=pbl
                        pbl=h(s2(7));  # Else, choose the next maximum                   
                
                
                ## For nighttime
                
                if j>sunsix:
                    pbl=nan;                
                
                # Allocate to daily file
                pbl24(j)=pbl; 
            else
            disp(['day ' num2str(i) ', hour ' num2str(j) ', channel ' num2str(m) ' not computed. ' num2str(sum(isnan(s(1:30)))) ' nans in lower 30 points'])    
            
        
        ## Allocate to annual file
        
        if nansum(negSNR)>4:
            pbl24=nan(24,1);       
       
        if i==day_end:
            PBL(daysun3==i)=pbl24(1:end-5);
            SUNSIX(daysun3==i)=ssix(1:end-5);
        else
            PBL(daysun3==i)=pbl24;
            SUNSIX(daysun3==i)=ssix;
   
    ALL(:,m)=PBL;# Allocate to table with all channels


## Plot the 3 channels and their variability

date=plottime;
doy=doy;

PBL_cam0=nanmean(ALL,2);# Raw mean of PBL height from the three channels
PBL_cam0(daynight==0,:)=nan;
PBL_SD=nanstd(ALL,[],2); # Standard deviation from the three channels
n=sum(~isnan(ALL),2);

figure;
plot(date,ALL(:,1),'.-');hold on
plot(date,ALL(:,2),'.-');
plot(date,ALL(:,3),'.-');ylabel('PBL heigth (km)')
hold on;plot(date,PBL_SD);
legend('SNR_1','SNR_2','SNR_3','Stand. Dev')
title('SNR from three channels and their variation')
