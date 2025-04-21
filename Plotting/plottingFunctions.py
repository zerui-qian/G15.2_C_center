# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 11:54:11 2024

@author: Johannes Eberle and Nikki
@functionality: Contains functions that might be needed to load and plot data
"""
import numpy as np
import re
from datetime import datetime
import os
import json
import h5py
import matplotlib.pyplot as plt
import sys
sys.path.append(os.path.abspath(r'F:/Users/QPG/Documents/zerui_g15/C-hBN_new/Logging'))
import save
from matplotlib.colors import LogNorm
import io
from PIL import Image
from scipy.optimize import curve_fit


def get_filename_by_index_and_date(base_folder, date, index):
    """
    Constructs the filenames (HDF5 and log) based on the date and index.

    Args:
        base_folder (str): The base folder where data is stored.
        date (str): The date in yyyy-mm-dd format.
        index (int): The index of the file to load.

    Returns:
        tuple: Full paths to the HDF5 file and the log file.
    """
    date_folder = os.path.join(base_folder, date)

    if not os.path.exists(date_folder):
        raise FileNotFoundError(f"The specified date folder does not exist: {date_folder}")

    h5_file = None
    log_file = None

    # Look for files with the given index
    for filename in os.listdir(date_folder):
        if filename.startswith(f"{index}_"):
            if filename.endswith(".h5"):
                h5_file = os.path.join(date_folder, filename)
            elif filename.endswith(".json"):
                log_file = os.path.join(date_folder, filename)

    if h5_file is None:
        raise FileNotFoundError(f"No HDF5 file found with index {index} in folder {date_folder}")

    if log_file is None:
        raise FileNotFoundError(f"No log file found with index {index} in folder {date_folder}")

    return h5_file, log_file

def save_figure(fig, data_file, processed_base_path = r"Z:\\Projects\\Defects for QTM\\Processed_data_zerui" ):
    """
    Saves the figure with a filename based on the data file name and an additional index.

    Args:
        fig (matplotlib.figure.Figure): The figure to save.
        data_file (str): The path to the data file (HDF5).

    Returns:
        str: Full path to the saved figure.
    """
    # Define the base path for processed data
    

    # Extract date from the data file path
    base_folder, filename = os.path.split(data_file)
    date_folder = os.path.basename(os.path.dirname(data_file))
    processed_date_folder = os.path.join(processed_base_path, date_folder)

    # Create the date folder if it does not exist
    os.makedirs(processed_date_folder, exist_ok=True)

    # Generate the filename base
    filename_base, _ = os.path.splitext(filename)

    # Create a unique filename for the figure
    figure_index = 1
    while True:
        figure_filename = f"{filename_base}_{figure_index}.png"
        figure_path = os.path.join(processed_date_folder, figure_filename)
        if not os.path.exists(figure_path):
            break
        figure_index += 1

    fig.savefig(figure_path)

    
#def plot_APDscan(filename):
#    """Create a scatter plot for APD scan data and return the figure."""
#    x = save.load_data(filename)
#    Loc = x['locations']
#    PC0 = x['PC0']
#    PC1 = x['PC1']
#    apd = PC0 + PC1
#
#    maxcounts = max(apd)  # Set maximum counts for color scale
#
#    # Create the figure
#    fig, ax = plt.subplots()
#    scatter = ax.scatter(Loc[:, 0], Loc[:, 1], c=apd, cmap='Blues', vmin=0, vmax=maxcounts)
#    colorbar = fig.colorbar(scatter, ax=ax, label='Counts')
#    ax.set_xlabel('X-coordinate, V')
#    ax.set_ylabel('Y-coordinate, V')
#    ax.set_title(f'APD map \n {os.path.basename(filename)}')
#
#    # Return the figure
#    return fig

def plot_APDscan(filename, size=(14,4), clip=False, clipNumber=1000):
    """
    Create side-by-side scatter plots for APD scan data with linear and logarithmic scales.
    
    Parameters:
        filename (str): Path to the file containing the data.
        clip (bool): Whether to clip values at a specified limit.
        clipNumber (int): The maximum value to clip the data, used if clip=True.
    
    Returns:
        matplotlib.figure.Figure: The generated scatter plot figure.
    """
    # Load data
    x = save.load_data(filename)
    Loc = x['locations']
    
    if x.get('PC0') is not None:  
        PC0 = x['PC0']
        PC1 = x['PC1']
        apd = PC0 + PC1  # Total counts
    else:
        apd = x.get("apd_counts")
    
    # Adjust data for clipping if requested
    if clip:
        apd = np.clip(apd, 0, clipNumber)
    
    sorted_indices = np.argsort(Loc[:, 0])  # Sort by x-coordinate
    Loc_sorted = Loc[sorted_indices]
    apd_sorted = apd[sorted_indices]
    x_unique = np.unique(Loc_sorted[:, 0])
    y_unique = np.unique(Loc_sorted[:, 1])
    X, Y = np.meshgrid(x_unique, y_unique)
    
    # Create an empty grid for the APD values
    apd_grid = np.zeros_like(X)
    for i in range(len(Loc_sorted)):
        x_idx = np.searchsorted(x_unique, Loc_sorted[i, 0])
        y_idx = np.searchsorted(y_unique, Loc_sorted[i, 1])
        apd_grid[y_idx, x_idx] = apd_sorted[i]
    
    # Compute physical dimensions
    x_range = max(x_unique) - min(x_unique)
    y_range = max(y_unique) - min(y_unique)

    # Set base figure size
    fig_width = 6  # Base height of the figure
    aspect_ratio = y_range / x_range if y_range != 0 else 1
    fig_height = fig_width * aspect_ratio

    # Set up figure with two subplots
    fig, axes = plt.subplots(1, 2, figsize=(size[0], size[1]), constrained_layout=True)

    # Linear scale plot
    scatter_linear = axes[0].pcolormesh(X, Y, apd_grid, cmap='magma', vmin=min(apd), vmax=max(apd))
    colorbar_linear = fig.colorbar(scatter_linear, ax=axes[0], label='Count rate (Hz)')
    axes[0].set_xlabel(r'SCx (V)')
    axes[0].set_ylabel(r'SCy (V)')
    axes[0].set_title(f'APD Map (Linear Scale)\n {os.path.basename(filename)}')

    # Logarithmic scale plot
    scatter_log = axes[1].pcolormesh(X, Y, apd_grid, cmap='magma', norm=LogNorm(vmin=min(apd), vmax=max(apd)))
    colorbar_log = fig.colorbar(scatter_log, ax=axes[1], label='Count rate (Hz, log scale)')
    axes[1].set_xlabel('SCx (V)')
    axes[1].set_ylabel('SCy (V)')
    axes[1].set_title(f'APD Map (Logarithmic Scale)\n {os.path.basename(filename)}')
    
    for ax in axes:
        ax.set_box_aspect(aspect_ratio)  # Only scale axes


    return fig

def plot_XYZ_APDscan(filename, clip=False, clipNumber=1000):
    """
    Create side-by-side scatter plots for APD scan data with linear and logarithmic scales.
    Returns: matplotlib.figure.Figure: The generated scatter plot figure.
    """
    # Load data
    x = save.load_data(filename)
    time_vals = x.get('time_vals')
    count_vals = x.get('count_vals')
    xyz_optimun_vals = x.get('xyz_optimun_vals')
    
    # Set up figure with two subplots
    fig, axes = plt.subplots(2, 3, figsize=(12, 6), constrained_layout=True)
    
    axes[0, 0].axis('off')
    axes[0, 2].axis('off')

    # Linear scale plot
    plot_linear = axes[0,1].plot(time_vals, count_vals, c= 'firebrick')
    axes[0,1].set_xlabel('Time (s)')
    axes[0,1].set_ylabel('Count rate (counts/s)')
    axes[0,1].set_title(f'XYZ APD\n {os.path.basename(filename)}')
    
    axisNames = ["x", "y", "z"]
    for i in range(3):
        a = np.arange(np.shape(xyz_optimun_vals)[0])
        plot_linear = axes[1,i].scatter(a, xyz_optimun_vals[:,i], c= 'firebrick')
        axes[1,i].set_xlabel('Iteration')
        axes[1,i].set_ylabel('Optimum position')
        axes[1,i].set_title(f'Recovered maximum count rate\nin {axisNames[i]}-axis')
    
    return fig


def plot_APDscan_with_shift(filename, x_shift=0, clip=False, clipNumber=1000, clipLow=False, clipMin = 2000):
    """
    Create scatter plots for APD scan data with manual x-direction shifts for odd rows.
    
    Parameters:
        filename (str): Path to the file containing the data.
        x_shift (float): The amount by which to shift odd rows in the x-direction.
        clip (bool): Whether to clip values at a specified limit.
        clipNumber (int): The maximum value to clip the data, used if clip=True.
    
    Returns:
        matplotlib.figure.Figure: The generated scatter plot figure.
    """
    # Load data
    x = save.load_data(filename)
    Loc = x['locations']
    
    if x.get('PC0') is not None:  
        PC0 = x['PC0']
        PC1 = x['PC1']
        apd = PC0 + PC1  # Total counts
    else:
        apd = x.get("apd_counts")
    
    # Adjust data for clipping if requested
    if clip:
        apd = np.clip(apd, 0, clipNumber)
    if not clipLow:
        clipMin = 0
    
    # Apply x_shift to odd rows based on y-coordinates
    y_unique = np.unique(Loc[:, 1])  # Unique y-values (rows)
    for i, y_val in enumerate(y_unique):
        if i % 2 == 1:  # Odd rows
            mask = Loc[:, 1] == y_val
            Loc[mask, 0] += x_shift  # Shift x-coordinates for these rows
    
    # Set up figure with two subplots
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)

    # Linear scale plot
    scatter_linear = axes[0].scatter(
        Loc[:, 0], Loc[:, 1], c=apd, cmap='Blues', vmin=clipMin, vmax=max(apd)
    )
    colorbar_linear = fig.colorbar(
        scatter_linear, ax=axes[0], label='Count rate (Hz)'
    )
    axes[0].set_xlabel('X-coordinate (V)')
    axes[0].set_ylabel('Y-coordinate (V)')
    axes[0].set_title(f'APD Map (Linear Scale)\n {os.path.basename(filename)}')

    # Logarithmic scale plot
    scatter_log = axes[1].scatter(
        Loc[:, 0], Loc[:, 1], c=apd, cmap='Blues', norm=LogNorm(vmin=1, vmax=max(apd))
    )
    colorbar_log = fig.colorbar(
        scatter_log, ax=axes[1], label='Count rate (Hz, log scale)'
    )
    axes[1].set_xlabel('X-coordinate (V)')
    axes[1].set_ylabel('Y-coordinate (V)')
    axes[1].set_title('APD Map (Logarithmic Scale)\n {os.path.basename(filename)}')

    return fig

def plot_APDscan_without_every_second_row(filename, clip=False, clipNumber=1000, clipLow=False, clipMin=2000, parity=0):
    """
    Create scatter plots for APD scan data with every second row removed to mitigate hysteresis effects.

    Parameters:
        filename (str): Path to the file containing the data.
        clip (bool): Whether to clip values at a specified limit.
        clipNumber (int): The maximum value to clip the data, used if clip=True.
        clipLow (bool): If False, forces the lower clipping limit to zero.
        clipMin (float): The minimum value for clipping (only used if clipLow=True).

    Returns:
        matplotlib.figure.Figure: The generated scatter plot figure.
    """


    # Load data
    x = save.load_data(filename)
    Loc = x['locations']

    if x.get('PC0') is not None:  
        PC0 = x['PC0']
        PC1 = x['PC1']
        apd = PC0 + PC1  # Total counts
    else:
        apd = x.get("apd_counts")

    # Apply clipping if requested
    if clip:
        apd = np.clip(apd, 0, clipNumber)
    if not clipLow:
        clipMin = 0

    # Remove every second row based on y-coordinates.
    # First, get the sorted unique y-values (each representing a row).
    y_unique = np.unique(Loc[:, 1])
    # Build a boolean mask to keep only rows with even-indexed y values.
    keep_mask = np.zeros(Loc.shape[0], dtype=bool)
    for i, y_val in enumerate(y_unique):
        if i % 2 == parity:  # Keep rows corresponding to even-indexed y values.
            keep_mask |= (Loc[:, 1] == y_val)
    
    # Apply the mask to the data arrays
    Loc = Loc[keep_mask]
    apd = apd[keep_mask]

    # Set up figure with two subplots
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)

    # Linear scale plot
    scatter_linear = axes[0].scatter(
        Loc[:, 0], Loc[:, 1], c=apd, cmap='Blues', vmin=clipMin, vmax=apd.max()
    )
    fig.colorbar(scatter_linear, ax=axes[0], label='Count rate (Hz)')
    axes[0].set_xlabel('X-coordinate (V)')
    axes[0].set_ylabel('Y-coordinate (V)')
    axes[0].set_title(f'APD Map (Linear Scale)\n{os.path.basename(filename)}')

    # Logarithmic scale plot
    scatter_log = axes[1].scatter(
        Loc[:, 0], Loc[:, 1], c=apd, cmap='Blues', norm=LogNorm(vmin=1, vmax=apd.max())
    )
    fig.colorbar(scatter_log, ax=axes[1], label='Count rate (Hz, log scale)')
    axes[1].set_xlabel('X-coordinate (V)')
    axes[1].set_ylabel('Y-coordinate (V)')
    axes[1].set_title(f'APD Map (Logarithmic Scale)\n{os.path.basename(filename)}')

    return fig

def nm_to_eV(wlens):
    h = 6.62607015e-34
    c = 299792458
    e = 1.602176634e-19
    return (1e9*h*c/e) / wlens


def plot_spectrum(filename, xlim=(1.7,2.3), ymax=None):
    """Create a plot for spectrum data and return the figure."""
    x = save.load_data(filename)
    wavelengths = np.array(x['wavelength'])
    signals = np.array(x['intensity'])
    
    # Convert to energy
    energy = nm_to_eV(wavelengths)

    # Debug prints
    print(f"Loaded wavelengths: {wavelengths.shape}, min={np.min(wavelengths)}, max={np.max(wavelengths)}")
    print(f"Converted energy: {energy.shape}, min={np.min(energy)}, max={np.max(energy)}")
    print(f"Raw signals: {signals.shape}, min={np.min(signals)}, max={np.max(signals)}")

    # Fix signal shape
    if signals.ndim == 3 and signals.shape[0] == 1:
        signals = signals[0]
    signals = signals.squeeze()
    
    # Ensure correct shapes
    if energy.shape != signals.shape:
        print("Mismatch in shapes! Flattening arrays.")
        energy = energy.flatten()
        signals = signals.flatten()

    # Debugging after processing
    print(f"Processed signals: {signals.shape}, min={np.min(signals)}, max={np.max(signals)}")

    fig = plt.figure(figsize=(12,5.5))
    plt.plot(energy, np.abs(signals), color="k", linewidth=0.9)
    
    # Auto-adjust ymax if not provided
    ymax = np.max(np.abs(signals)) * 1.1 if ymax is None else ymax
    plt.ylim(0, ymax)

    plt.title(f'Spectrum measurement {os.path.basename(filename)}')
    plt.xlabel("E (eV)")
    plt.ylabel("Counts")
    plt.grid(True)
    
    ax1 = plt.gca()
    ax2 = ax1.twiny()
    
    wl_ticks = np.arange(540, 725, 10)
    energy_ticks_for_wl = nm_to_eV(wl_ticks)
    
    ax1.set_xticks(np.arange(xlim[0], xlim[1], 0.05))
    ax1.set_xlim(xlim)
    
    ax2.set_xticks(energy_ticks_for_wl)
    ax2.set_xticklabels([f'{e:.0f}' for e in wl_ticks])
    ax2.set_xlim(xlim)
    ax2.set_xlabel(r'$\lambda$ (nm)')

    return fig

def plot_angles(filename, ymin=50000):
    x = save.load_data(filename)
    angles = np.array(x['angles']) * 2
    angles = np.deg2rad(angles)
    counts = np.array(x['apd_counts'])

    fig = plt.figure(figsize=(4,4))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, counts, "k.")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rlim(ymin, max(counts))
    ax.set_title(f'Polarization measurement {os.path.basename(filename)}')
    plt.grid(True)

    return fig


def lorentzian(x, A, x0, gamma):
    return -A / (1 + ((x - x0) / gamma)**2)

def ODMR_sweep(filename):
    x = save.load_data(filename)
    if x.get('freq_range').all != None:
        freq = x['freq_range']
        nomalized_counts = x['normalized']
        x_shape = 1
    else:
        all_freq = x['freq_arr']
        all_nomalized_counts = x['normalized_arr']
        x_shape = np.shape(all_nomalized_counts)[0]
        freq = all_freq[0,:]
        nomalized_counts = np.sum(all_nomalized_counts,axis=0) / np.shape(all_nomalized_counts)[0]
    
   
    fig = plt.figure()
    
    #lorentzian fit
    
    # down_size_freq = freq[250:300]
    # down_size_nomalized_counts = nomalized_counts[250:300]
    
    # # Estimate the initial guesses
    # # A_guess = np.min(down_size_nomalized_counts)  # Initial guess for Amplitude
    # # x0_guess = down_size_freq[np.argmin(down_size_nomalized_counts)]  # Initial guess for Center (x0)
    # # gamma_guess = (down_size_freq[-1] - down_size_freq[0]) / 4  # Initial guess for Gamma (width)

        
    # # popt, pcov = curve_fit(lorentzian, down_size_freq, down_size_nomalized_counts,
    # #                         p0=[A_guess, x0_guess, gamma_guess])
    # # A_fit, x0_fit, gamma_fit = popt
    # # y_fit = lorentzian(down_size_freq, A_fit, x0_fit, gamma_fit)
 
    # # plt.plot(down_size_freq, y_fit, 'r-', label='Lorentzian fit')  # Plot the fitted Lorentzian curve
    # plt.plot(down_size_freq, down_size_nomalized_counts, 'b.', label='Data')  # Plot the noisy data
    
    plt.plot(freq, nomalized_counts, 'b.', label='Data')  # Plot the noisy data
    if x.get('repetition') is not None:
        N = x['freq_range']
        plt.title(f'Averaged ODMR of {N} iterations with drift correction')
    else:
        plt.title(f'Averaged ODMR of {x_shape} iterations with drift correction')
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('APD count rate (counts/s)')
        
    # nomalized_counts = np.sum(nomalized_counts,axis=0) / np.shape(nomalized_counts)[0]
    # N = x['repetition']
    return fig

    
    
def plot_PLE(filename):
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