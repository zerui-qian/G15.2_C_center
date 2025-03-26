# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 14:26:46 2025

@author: QPG
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.colors import Normalize
from matplotlib import cm

# Define the directory to save the plots
Path = 'Z:\\Projects\\Defects for QTM\\Processed data\\2025-01-23\\'
plot_save_path = os.path.join(Path, "Spectra_Plots")
os.makedirs(plot_save_path, exist_ok=True)

# Load the data
data_folder = 'Z:\\Projects\Defects for QTM\\Raw data\\2025-02-05\\'
loc_data = pd.read_csv(data_folder + 'Loc_hBNPLscan_90BS 0.7NA Mapping T=4 K Power=25 uW Exposuretime=20 s filter 434BP and 475BP 25-02-05-08-33-14.csv')
spec_data = pd.read_csv(data_folder + 'Spec_hBNPLscan_90BS 0.7NA Mapping T=4 K Power=25 uW Exposuretime=20 s filter 434BP and 475BP 25-02-05-08-33-14.csv')
wav_data = pd.read_csv(data_folder + 'Wav_hBNPLscan_90BS 0.7NA Mapping T=4 K Power=25 uW Exposuretime=20 s filter 434BP and 475BP 25-02-05-08-33-14.csv')

# Ensure data is in numpy arrays for easier manipulation
loc_array = loc_data.values
spec_array = spec_data.values

# Calculate the maximum intensity for each spectrum
max_intensities = spec_array.max(axis=1)

# Extract x and y coordinates
x_coords = loc_array[:, 0]
y_coords = loc_array[:, 1]

# Define clipping values
min_value = 40  # Adjust as needed
max_value = 80  # Adjust as needed

# Clip the maximum intensities
clipped_intensities = np.clip(max_intensities, min_value, max_value)

# Create a scatter plot of the clipped intensities
plt.figure(figsize=(10, 8))
scatter = plt.scatter(x_coords, y_coords, c=clipped_intensities, cmap="viridis", s=50, edgecolor="k")
plt.colorbar(scatter, label="Maximum Intensity (Clipped)")
plt.xlabel("X Location")
plt.ylabel("Y Location")
plt.title("Clipped Maximum Intensity of Spectra at Each Location")
plt.grid()

# Save the plot
output_plot_path = os.path.join(Path, "Clipped_Maximum_Intensity_Map.png")
plt.savefig(output_plot_path)
plt.show()

print(f"Clipped maximum intensity map saved as {output_plot_path}")
