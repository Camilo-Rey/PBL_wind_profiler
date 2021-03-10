# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 18:53:23 2020

@author: VinnieRibeiro and CamiloRey
"""

# # Download raw data of NOAA wind profiler
# ## By Vinnie Ribeiro and Camilo Rey
# ### Dec 27, 2019
# #### This code 1) downloads a selected subset of the raw data of the NOAA wind profiler from the NOAA ftp server and stores it in the local machine. 

# Import libraries

import pandas as pd
import os
import numpy as np
import ftplib
import io
import time


# Parameters input
site='tci'
year=2020
yr=str(year)


# Dowload data from NOAA and store it in current working directory

ftp = ftplib.FTP("ftp1.esrl.noaa.gov")
ftp.login()

base = f'/psd2/data/realtime//Radar915/WwWind/{site}/'

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
print(f'Time without skipping already downloaded files : {t_final-t_init}')