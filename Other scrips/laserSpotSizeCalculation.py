# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 00:48:21 2025

@author: QPG
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
import json
from datetime import datetime
import sys
sys.path.append(os.path.abspath(r'C:\Users\QPG\Documents\Python Scripts\johannes\Control code\Logging'))
sys.path.append(os.path.abspath(r'C:\Users\QPG\Documents\Python Scripts\johannes\Control code\Plotting'))
import save
import plottingFunctions

def gaussian(x, a, x0, sigma, c):
    """Gaussian function for fitting."""
    return a * np.exp(-(x - x0)**2 / (2 * sigma**2)) + c

def analyze_spot_size(filename, y_value, conversion_factor):
    """
    Analyzes the spot size by taking a single row of data, plotting the counts vs x position,
    and fitting a Gaussian function to determine the spot size.

    Parameters:
        data (numpy.ndarray): 2D array containing scan data.
        row_number (int): The row index to analyze.
        conversion_factor (float): Conversion factor from voltage to micrometers.

    Returns:
        dict: Fitting results including spot size (FWHM), peak position, and fit parameters.
    """
    # load data
    x = save.load_data(filename)
    loc = x['locations']
    PC0 = x['PC0']
    PC1 = x['PC1']
    data = PC0 + PC1  # Total counts
    
       # Ensure data is reshaped correctly for analysis
    unique_y = np.unique(loc[:, 1])  # Unique y positions

    # Find the closest y value in the dataset
    closest_y = unique_y[np.argmin(np.abs(unique_y - y_value))]

    # Extract indices corresponding to the chosen y value
    indices = np.where(loc[:, 1] == closest_y)[0]

    # Extract x positions and data for the selected y value
    x_positions = loc[indices, 0] * conversion_factor
    row_data = data[indices]
    # Initial guesses for Gaussian fitting
    initial_guess = [np.max(row_data), x_positions[np.argmax(row_data)], conversion_factor, row_data[-1]]

    # Fit the data with a Gaussian
    try:
        popt, pcov = curve_fit(gaussian, x_positions, row_data, p0=initial_guess, bounds=([0, -np.inf, 0, 0], [np.inf, np.inf, np.inf, np.inf]))
        
        # Extract fitted parameters
        amplitude, peak_position, sigma, c= popt
        fwhm = 2.355 * sigma  # Convert sigma to FWHM
        parameter_errors = np.sqrt(np.diag(pcov))  # Standard errors of the parameters
        print(parameter_errors)
        # Plot the data and the fit
        plt.figure(figsize=(8, 6))
        plt.plot(x_positions, row_data, 'b-', label='Data')
        plt.plot(x_positions, gaussian(x_positions, *popt), 'r--', label='Gaussian Fit')
        plt.title(f'Row {row_number}: Spot Size Analysis')
        plt.xlabel('Position (µm)')
        plt.ylabel('Counts')
        plt.legend()
        plt.grid()
        plt.show()

        # Return fitting results
        return {
            "Amplitude": amplitude,
            "Peak Position (µm)": peak_position,
            "Spot Size (FWHM, µm)": fwhm,
            "Fit Parameters": popt
        }
    except Exception as e:\        print(f"Error during fitting: {e}")
        return None

# Example usage:
# Assume `scan_data` is a 2D numpy array, row_number is the row to analyze, and conversion_factor is given
row_number = 6.32  # Example row number
conversion_factor = 5.787594475  # conversion factor (volts to micrometers)
        
# Variables to specify
base_folder = 'Z:\\Projects\\Defects for QTM\\Raw data\\'
date = '2024-12-19'  # Specify the date in yyyy-mm-dd format
index = 29  # Specify the index of the file to plot

# Get the filename based on the date and index
data_file, log_file = plottingFunctions.get_filename_by_index_and_date(base_folder, date, index)

results = analyze_spot_size(data_file, row_number, conversion_factor)
print(results)