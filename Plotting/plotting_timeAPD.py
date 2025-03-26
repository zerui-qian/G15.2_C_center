# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 21:57:44 2024

@author: Johannes Eberle
@functionality: Plot the APD counts vs. time
"""
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(os.path.abspath(r'C:\Users\QPG\Documents\Python Scripts\johannes\Control code\Plotting'))
import plottingFunctions
import pandas as pd
##############################################################################
# Choose here which data to plot

dates = ['2024-11-03']
files = [-1]

##############################################################################

# An array of dictionaries.Each dictionary contains a data set
#data = plottingFunctions.load_measurements(dates, files)
# Define the path to your CSV file
folder = 'Z:\\Projects\\Defects for QTM\\Raw data\\2025-02-20\\'
filename = 'ExperimentalAPDcountwithtime_hBN_chip45_f15_20250304_163210 - Copy (2).csv'  # Example filename, update to your actual filename

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(folder + filename)
times = df['Time'].to_numpy() / 60 # Access "Time" column
apd_counts = df['APD counts'].to_numpy()  # Access "APD counts" column



plt.figure(figsize=(10, 6))

plt.plot(times, apd_counts, color="blue", linestyle="-")

# Adding labels and title
plt.title("APD Count Rate vs Time")
plt.xlabel("Time (hours)")
plt.ylabel("APD count rate (cps)")
plt.grid(True)
plt.legend()
#plottingFunctions.save(dates, files)

# Show the plot
plt.show()
