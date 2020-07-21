# PBL_wind_profiler
By Camilo Rey-Sanchez and Vinnie Ribeiro

Download, read, and process raw data from NOAA wind profiler to calculate hourly or half-hourly planetary boundary layer height (PBL) also known as atmospheric boundary layer (ABL). 

SUMMARY
1) Use Download_NOAA_data.py to download data from NOAA's network of radar wind profilers. 
2) Use SNR_raw_read.py to extract the signal-to-noise ratio (SNR) from the wind profiler data downloaded in the previous step. Select year of interest.
3) Use Process_SNR.py to process the SNR values from the previous step and calculate PBL height. The data usually comes in hourly time steps but sometimes it comes in half-hourly time steps. 

HOW TO USE
1) Use Download_NOAA_data.py to download data from NOAA's network of radar wind profilers 
   This code downloads a selected subset of the raw data of the NOAA wind profiler from the NOAA ftp server and stores it in the local machine.
	Modify site of interest (3-letter code used by NOAA to identify the stations. e.g. 'tci')
	Modify year of interest. The code downloads all the files within that year (this can take several minutes-up to 1 hour).
2) Use SNR_raw_read.py to extract the signal-to-noise ratio (SNR) from the wind profiler data downloaded in the previous step.
	Modify site of interest (3-letter code used by NOAA to identify the stations. e.g. 'tci')
	Modify year of interest.
	Modify 'currdir': directory where data downloaded from previous step is located.
	Modify 'res': Resolution of the profiler. Fine=1, Coarse=2
	
3) Use Process_SNR.py to process the SNR values from the previous step and calculate PBL height.
	Modify year of interest.
	Modify name of .npz dataset generated in previous step if necessary.

The process was done in Spyder 4.0.1 and Python 3.7.1 64-bit | Qt 5.9.6 | PyQt5 5.9.2 | Windows 10

Packages and functions needed to run this code include:

numpy 1.18.1
pandas  0.25.3
matplotlib 3.1.1
pytz 2019.3

To replicate the full environment see accompanying file environment.yml