# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 21:28:57 2025

@author: Nikki, Johannes and a bit of ChatGPT
"""

import time
import numpy as np
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(r'D:\Users\QPG G8.1\Documents\Python Scripts\Johannes github code\Devices'))
sys.path.append(os.path.abspath(r'D:\Users\QPG G8.1\Documents\Python Scripts\Johannes github code\Measurements'))
import DeviceManager
from measurements_APDscan import scan_area
from tqdm import tqdm

def perform_area_scan_with_rf(params, DM, rf_on=False, frequency=None):
    """
    Perform an area scan to find the optimal position. Optionally with the RF signal generator on.
    """
    gm = DM.devices.get("daq_ao")
    sg = DM.devices.get('RFSignalGenerator')
    
    # Set RF signal generator state
    if rf_on:
        if frequency is not None:
            sg.set_frequency(frequency)  # Set the RF frequency
        sg.switch_output(1)  # Turn on the RF signal generator
    else:
        sg.switch_output(0)  # Turn off the RF signal generator

    # Perform the area scan (this is just a placeholder for your area scan logic)
    data, DM = scan_area(params, DM)  # Assuming scan_area returns the best location as part of 'data'
    
    # Retrieve the best position from the scan
    best_xy = data.get('best_xy_loc')
    
    return best_xy, DM

def perform_apd_counts(apd, sg, rf_on=False):
    """
    Perform APD count measurement. Optionally with RF signal generator on.
    """
    if rf_on:
        sg.switch_output(1)  # Turn on RF signal generator
    else:
        sg.switch_output(0)  # Turn off RF signal generator

    # Get the APD counts at the current position
    apd_counts = apd.GetCountRate()
    
    return apd_counts

def Combined_XYZ_RF_sweep(params, DM):
    # Initialize devices
    gm = DM.devices.get("daq_ao")
    apd = DM.devices.get("apd")
    sg = DM.devices.get('RFSignalGenerator')

    # Prepare arrays to store data
    freq_arr = []
    normalized_arr = []
    optimal_positions = []  # Will hold positions and counts for RF OFF and RF ON scans
    timestamps = []

    # Create the frequency range for the sweep
    frequency_range = np.linspace(
        params.get("start"), 
        params.get("stop"), 
        int((params.get("stop") - params.get("start")) / params.get("stepsize")) + 1
    )

    for frequency in frequency_range:
        print(f"\nProcessing frequency {frequency} Hz at {datetime.now().strftime('%H:%M:%S')}")
        
        # ----- RF OFF scan -----
        print("Performing area scan with RF signal generator OFF")
        best_xy_off, DM = perform_area_scan_with_rf(params, DM, rf_on=False)
        params['scan_center'] = (best_xy_off[0], best_xy_off[1])
        
        gm.set_ao0(best_xy_off[0])
        gm.set_ao1(best_xy_off[1])
        
        apd_counts_off = perform_apd_counts(apd, sg, rf_on=False)
        print(f"APD counts with RF OFF: {apd_counts_off}")

        # ----- RF ON scan -----
        print("Performing area scan with RF signal generator ON")
        # Use the RF OFF best position as the center for the RF ON scan
        params['scan_center'] = (best_xy_off[0], best_xy_off[1])
        
        best_xy_on, DM = perform_area_scan_with_rf(params, DM, rf_on=True, frequency=frequency)
        params['scan_center'] = (best_xy_on[0], best_xy_on[1])
        
        gm.set_ao0(best_xy_on[0])
        gm.set_ao1(best_xy_on[1])
        
        apd_counts_on = perform_apd_counts(apd, sg, rf_on=True)
        print(f"APD counts with RF ON (Frequency {frequency} Hz): {apd_counts_on}")

        # Compute APD ratio (RF ON / RF OFF)
        ratio = apd_counts_on / apd_counts_off if apd_counts_off > 0 else 0
        normalized_arr.append(ratio)
        freq_arr.append(frequency)
        
        optimal_positions.append({
            'frequency': frequency,
            'rf_off_position': best_xy_off,
            'rf_on_position': best_xy_on,
            'apd_counts_off': apd_counts_off,
            'apd_counts_on': apd_counts_on,
            'ratio': ratio
        })
        timestamps.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # Prepare the final combined data
    data = {
        'freq_arr': freq_arr,
        'ODMR_SPE': normalized_arr,
        'optimal_positions': optimal_positions,
        'timestamps': timestamps,
        'additional_info': 'Single cycle combined XYZ optimization, RF sweeps, and APD scans (RF OFF then RF ON for each frequency without depth scan)'
    }

    return data, DM