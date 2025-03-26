# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 18:09:52 2025

@author: QPG
"""

import numpy as np
import time
import Pyro4
import pandas as pd
import os

# Pyro4 configuration
Pyro4.config.SERIALIZER = 'serpent'
Pyro4.config.SERIALIZERS_ACCEPTED = {'serpent', 'json', 'marshal', 'pickle'}

Path = r'Z:\Projects\Defects for QTM\Raw data\2025-01-21'
# Connects to WinSpec in G13
################

temp = 4  # K
e_time = 15  # s
power = 65  # uW

print('connect to ws')
uri = 'PYRO:WinSpec@G13-spectrometer.dhcp-int.phys.ethz.ch:9090'
ws = Pyro4.Proxy(uri)
print(ws)
ws.exposure_time = e_time
nFrames = 1
ws.num_frames = nFrames
print('spect ok')
###########################

x_step = 0.5 / 15
y_step = 0.5 / 15
x_number = 80
y_number = 60
Loc_start_x = 0
Loc_start_y = 0
Loc_start = [Loc_start_x, Loc_start_y]

# Create file names using a timestamp and your naming scheme
timestamp = time.strftime("%y-%m-%d-%H-%M-%S", time.localtime())
name = "hBNPLscan_90BS 0.7NA Mapping T=%s K Power=%s uW Exposuretime=%s s filter 434BP and 475BP %s" % (temp, power, e_time, timestamp)
filename_loc = os.path.join(Path, 'Loc_' + name + '.csv')
filename_spec = os.path.join(Path, 'Spec_' + name + '.csv')
filename_wav = os.path.join(Path, 'Wav_' + name + '.csv')
filename_para = os.path.join(Path, 'Para_' + name + '.csv')

# Optionally, remove any existing files from previous runs:
for fname in [filename_loc, filename_spec, filename_wav, filename_para]:
    if os.path.exists(fname):
        os.remove(fname)

# Loop over rows (y-direction)
for i in range(y_number):
    # Temporary lists to collect data for this row
    row_Loc = []
    row_Spec = []
    row_Wav = []
    row_Para = []
    
    # Loop over columns (x-direction)
    for j in range(x_number):
        if i % 2 == 0:
            Loc_x = Loc_start[0] + x_step * j
            Loc_y = Loc_start[1] + y_step * i
            daq.set_ao0(Loc_x)
            daq.set_ao1(Loc_y)
        else:
            Loc_x = Loc_start[0] + x_step * (x_number - j - 1)
            Loc_y = Loc_start[1] + y_step * i
            daq.set_ao0(Loc_x)
            daq.set_ao1(Loc_y)
            
        row_Loc.append([Loc_x, Loc_y])
        time.sleep(0.01)
        
        # Acquire spectrum and wavelength data from WinSpec
        buf = ws.get_spectrum(wlen=True)
        spec, w_array = np.array(buf)
        winSpec = ws.specdict
        row_Spec.append(spec[0])
        row_Wav.append(w_array)
        row_Para.append(winSpec)
        time.sleep(0.01)
        
        if j == 0:
            Progress = i / y_number
            print('Progress is %.2f%% at %s' % (Progress * 100, time.strftime("%y-%m-%d-%H-%M-%S", time.localtime())))
            
    # Convert the current row's data to DataFrames.
    df_loc = pd.DataFrame(row_Loc, columns=["Loc_x", "Loc_y"])
    df_spec = pd.DataFrame(row_Spec)
    df_wav = pd.DataFrame(row_Wav)
    df_para = pd.DataFrame(row_Para)
    
    # Append the row data to CSV files.
    # The header is written only if the file does not exist.
    df_loc.to_csv(filename_loc, mode='a', header=not os.path.exists(filename_loc), index=False, sep=',')
    df_spec.to_csv(filename_spec, mode='a', header=not os.path.exists(filename_spec), index=False, sep=',')
    df_wav.to_csv(filename_wav, mode='a', header=not os.path.exists(filename_wav), index=False, sep=',')
    df_para.to_csv(filename_para, mode='a', header=not os.path.exists(filename_para), index=False, sep=',')