# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 11:51:48 2025

@author: QPG
"""

import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Define the directory to save the plots
Path = 'Z:\\Projects\\Defects for QTM\\Processed data\\2025-03-10\\Spectrum Scan\\'
plot_save_path = os.path.join(Path, "Spectra_Plots")
os.makedirs(plot_save_path, exist_ok=True)

# Load the data
data_folder = 'Z:\\Projects\Defects for QTM\\Raw data\\2025-03-10\\Spectrum Scan\\'
loc_data = pd.read_csv(data_folder + 'Loc_hBNSpectrumScan T=4 K Power=230 uW Exposuretime=2525-03-07-09-53-25.csv')
spec_data = pd.read_csv(data_folder + 'Spec_hBNSpectrumScan T=4 K Power=230 uW Exposuretime=2525-03-07-09-53-25.csv')
wav_data = pd.read_csv(data_folder + 'Wav_hBNSpectrumScan T=4 K Power=230 uW Exposuretime=2525-03-07-09-53-25.csv')

# Ensure data is in numpy arrays for easier manipulation
loc_array = loc_data.values
spec_array = spec_data.values
wav_array = wav_data.values

# Iterate through the spectra and save plots
for idx, (x, y) in enumerate(loc_array):
    plt.figure()
    plt.plot(wav_array[idx, :], spec_array[idx, :], label=f"Spectrum at ({x:.2f}, {y:.2f})")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Intensity")
    plt.title(f"Spectrum at ({x:.2f}, {y:.2f})")
    plt.legend()
    plt.grid()

    # Save the plot
    plot_filename = f"Spectrum_{x:.2f}_{y:.2f}.png"
    plt.savefig(os.path.join(plot_save_path, plot_filename))
    plt.close()

print(f"All spectra plots have been saved in {plot_save_path}")
