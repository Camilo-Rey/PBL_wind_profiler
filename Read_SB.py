# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 13:36:13 2020

@author: jverfail
Modified by Camilo Rey
"""

import h5py
import pandas as pd
#from datetime import datetime, timedelta
import numpy as np


dnames = ['WD','H', 'LE', 'wc', 'wm', 'wq', 'wt']

hf = h5py.File(r'C:\Users\biomet\Box Sync\UC-Berkeley\Sherman_Barn\SB_2019365_L2.mat', 'r')
nrows = hf['data']['year'].size

df = pd.DataFrame();

for dn in dnames:
    df[dn] = hf['data'][dn][:].reshape((nrows,))


## Datetime variable
    
df['Mdate'] = hf['data']['Mdate'][:].reshape((nrows,))
unixTime=round((df.Mdate-719529)*86400)
utall=[]

for i in range(len(df['Mdate'])):
    ut=pd.Timestamp(unixTime[i], unit='s')
    utall.append(ut)    
   
df['datetime'] = utall

df.set_index('datetime')    
outname = r'C:\Users\biomet\Box Sync\UC-Berkeley\Sherman_Barn\SB_2019365_L2.csv'
df.to_csv(outname, float_format='%.3f', na_rep='nan')