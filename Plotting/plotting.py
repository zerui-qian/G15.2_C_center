# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 10:50:54 2024

@author: QPG
@functionality: Plot anything
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime
import sys
sys.path.append(os.path.abspath(r'F:/Users/QPG/Documents/zerui_g15/C-hBN_new/Logging'))
import save
import plottingFunctions


# Variables to specify
base_folder = 'Z:\\Projects\\Defects for QTM\\Raw_data_zerui\\'
date = '2025-03-26'  # Specify the date in yyyy-mm-dd format
#index = np.linspace(1,100,100,dtype=int)  # Specify the index of the file to plot
index = [15]
saving = True

for i in index:
    # Get the filename based on the date and index
    data_file, log_file = plottingFunctions.get_filename_by_index_and_date(base_folder, date, i)
    #data_file = base_folder + date + '\\measurements_2024-12-09_175341.h5'
    #measurement = "APD_scan"
    plt.style.use('default')
    with open(log_file, 'r') as file:
        measurement = json.load(file)[0]['measurement']
        
    if measurement == 'spectrum':
        fig = plottingFunctions.plot_spectrum(data_file)
    elif measurement == 'APD_scan' or 'APD_scan_attocube':
        fig = plottingFunctions.plot_APDscan(data_file, size=(14,3.5), clip=False, clipNumber=1400)
    #    fig = plottingFunctions.plot_APDscan_with_shift(data_file, x_shift=0,
    #                                                    clip=False, clipNumber=2000,
    #                                                    clipLow=False, clipMin = 3000)
    #    fig = plottingFunctions.plot_APDscan_without_every_second_row(data_file,
    #                                                                  clip=True, clipNumber=1000,
    #                                                                  clipLow=False, clipMin=2000,
    #                                                                  parity=1)
        
    if saving:
        plottingFunctions.save_figure(fig, data_file)