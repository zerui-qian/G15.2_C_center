# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 05:19:14 2024

@author: Johannes Eberle
@functionality: Plot a PLE scan
"""
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(os.path.abspath(r'C:\Users\QPG\Documents\Python Scripts\johannes\Control code\Plotting'))
import plottingFunctions

##############################################################################
# Choose here which data to plot

dates = ['2024-11-07']
files = [-1]

##############################################################################

# An array of dictionaries.Each dictionary contains a data set
data = plottingFunctions.load_measurements(dates, files)


wavelengths = []
signals = []

for data_i in data:
    wavelengths.append(np.array(data_i["Wavelength"]))
    signals.append(np.array(data_i["Signal"]))


# Plotting APD counts vs Time
plt.figure(figsize=(10, 6))

for i, wavelengths_i in enumerate(wavelengths):
    plt.plot(wavelengths_i, signals[i], color="blue", linestyle="-")

# Adding labels and title
plt.title("Spectrum")
plt.xlabel("Wavelength (nm)")
plt.ylabel("Signal (a.u.)")
plt.grid(True)
plt.legend()
plottingFunctions.save(dates, files)

# Show the plot
plt.show()



import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# Load the CSV file
folder = 'Z:\\Projects\\Defects subgroup\\Raw data\\04_11_2024\\'
#folder2 = 'Z:\\Projects\\Defects subgroup\\Raw data\\30_10_2024\\'
filename = 'wavelengths_20241104_194438.csv'
#filename2 = 'wavelengths_20241030_102241.csv'
#data2 = pd.read_csv(folder+filename)
#data = pd.read_csv(folder2+filename2)
data = pd.read_csv(folder+filename)
# Specify the row index you want to plot

# Extracting the data from the specified row
temperature = data["Temperature (Celsius)"].to_numpy()
power1 = data["Power (mW)"].to_numpy()
#power2 = data2["Power (mW)"].to_numpy()
#power = np.concatenate((power1,power2[:203]),axis=0)
power = power1

set_wavelength = data["Set wavelength (nm)"].to_numpy() / 2

measured_wavelength1 = data["Measured wavelength (nm)"].to_numpy() * 1e9 / 2
#measured_wavelength2 = data2["Measured wavelength (nm)"].to_numpy() * 1e9 / 2
#measured_wavelength = np.concatenate((measured_wavelength1,measured_wavelength2[:203]),axis=0)
measured_wavelength = measured_wavelength1

iteration_time = data["Iteration Time (s)"].to_numpy()
success= data["Successes"].to_numpy()
#laser_stability = data["Laser stability"].to_numpy()
laser_tunings = data["Laser tunings"].to_numpy()
tuning_problems = data["Tuning problems"].to_numpy()

counts1 = data["APD counts"].to_numpy()
#counts2 = data2["APD counts"].to_numpy()
#counts = np.concatenate((counts1,counts2[:203]),axis=0)
counts = counts1
#c = 3e8
## Define the Gaussian function
#def gaussian(x, a, x0, sigma, c):
#    return a * np.exp(-(x - x0)**2 / (2 * sigma**2)) + c
#
#initial_guess = [max(counts), np.mean(measured_wavelength), np.std(measured_wavelength), counts[0]]
#popt, pcov = curve_fit(gaussian, measured_wavelength, counts, p0=initial_guess)
#
## Get the fitted parameters
#a_fit, x0_fit, sigma_fit, c_fit = popt
#
## Generate fitted counts
#fitted_counts = gaussian(measured_wavelength, *popt)

# Plot the original data and the Gaussian fit
plt.figure(figsize=(8, 6))
plt.plot(measured_wavelength, counts, 'b-', label='Data')
#plt.plot(measured_wavelength2, counts2, 'r-', label='Data')
#plt.plot(measured_wavelength, fitted_counts, 'r--', label='Gaussian Fit ')
plt.xlabel('Wavelength')
plt.ylabel('Counts')
#plt.title('Gaussian Fit to Counts Data')
plt.legend()
plt.grid(True)
plt.show()

fig, ax1 = plt.subplots()
#a2 = ax1.twinx()
left, bottom, width, height = [0.58, 0.56, 0.3, 0.3]
ax2 = fig.add_axes([left, bottom, width, height])

ax1.plot(measured_wavelength, counts, 'midnightblue')
ax2.plot(measured_wavelength, power*1e3, 'darkgreen')
#ax1.plot(measured_wavelength2[:203], counts2[:203], 'b-')
#ax2.plot(measured_wavelength2[:203], power2[:203]*1e3, 'g-')

ax1.set_xlabel('Wavelength (nm)')
ax1.set_ylabel('Counts', color='b')
ax2.set_ylabel('Power ($\mu W$)', color='g')

plt.show()

## Calculate FWHM
#fwhm = 2 * np.sqrt(2 * np.log(2)) * sigma_fit
#print(f"FWHM: {fwhm}")

# Convert the wavelength array and x0_fit to frequency (GHz)
wavelength_m = measured_wavelength * 1e-9  # Convert wavelength from nm to meters
x0_fit_m = x0_fit * 1e-9  # Central wavelength (x0 from fit) in meters
frequency_ghz = (c / wavelength_m) * 1e-9  # Convert frequency from Hz to GHz
frequency_x0_fit = (c / x0_fit_m) * 1e-9  # Frequency corresponding to x0 (maximum of fit)

# Calculate detuning (difference from the center of the Gaussian fit)
detuning = frequency_ghz - frequency_x0_fit

# Generate fitted counts in terms of frequency
fitted_counts = gaussian(measured_wavelength, *popt)

# Plot detuning (in GHz) vs counts
plt.figure(figsize=(8, 6))
plt.plot(detuning, counts, 'b-', label='Data')
plt.plot(detuning, fitted_counts, 'r--', label='Gaussian Fit')
plt.xlabel('Detuning from Gaussian Fit Maximum (GHz)')
plt.ylabel('Counts')
plt.title('Counts vs Detuning from Gaussian Fit Maximum')
plt.legend()
plt.grid(True)
plt.axvline(x=0, color='black', linestyle='--')  # Optional: Add vertical line at detuning = 0
plt.show()

# Print the FWHM in wavelength and frequency
fwhm_wavelength = 2 * np.sqrt(2 * np.log(2)) * sigma_fit
print(f"FWHM (Wavelength): {fwhm_wavelength} nm")

lambda_0_m = x0_fit * 1e-9  # Central wavelength in meters
fwhm_frequency = (c * fwhm_wavelength * 1e-9) / (lambda_0_m ** 2)  # FWHM in frequency (GHz)
print(f"FWHM (Frequency): {fwhm_frequency} GHz")