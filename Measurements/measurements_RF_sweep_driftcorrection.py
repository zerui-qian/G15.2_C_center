# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 18:20:26 2025

@author: Nikki Braganza and Johannes and a bit of chatgpt
"""

import numpy as np
import time
import sys
import os
from datetime import datetime
from measurements_APDscan import scan_area, scan_depth

sys.path.append(os.path.abspath(r'D:\Users\QPG G8.1\Documents\Python Scripts\Johannes github code\Devices'))
sys.path.append(os.path.abspath(r'D:\Users\QPG G8.1\Documents\Python Scripts\Johannes github code\Measurements'))
import DeviceManager

def perform_RF_sweep(params, gm, apd, sg):
    start = params.get("start")
    stop = params.get("stop")
    stepsize = params.get("stepsize")
    amp = params.get("amplitude")
    N = params.get("repetition")

    sg.set_amplitude(amp)
    freq = np.linspace(start, stop, int((stop-start)/stepsize)+1)
    contrast_sum = np.zeros(len(freq))

    for n in range(N):
        print(f'RF Sweep repetition {n+1}/{N}')
        contrast = np.zeros(len(freq))
        for i, f in enumerate(freq):
            time.sleep(0.2)
            apd_counts_off = apd.GetCountRate()

            sg.set_frequency(f)
            sg.switch_output(1)
            time.sleep(0.2)
            apd_counts_on = apd.GetCountRate()
            sg.switch_output(0)

            contrast[i] = apd_counts_on / apd_counts_off

        contrast_sum += contrast

    normalized = contrast_sum / N
    resonance_idx = np.argmin(normalized)
    resonance = freq[resonance_idx]

    print(f"Found resonance at frequency {resonance} Hz")

    return freq, normalized, resonance

def Combined_XYZ_RF_sweep(params, DM):

    # Initialize devices
    gm = DM.devices.get("daq_ao")
    apd = DM.devices.get("apd")
    sg = DM.devices.get('RFSignalGenerator')

    # Prepare arrays to store data
    rf_sweep_results = []
    xyz_positions = []
    timestamps = []
    freq_arr = []
    normalized_arr = []
    resonance_arr = []
    optimized_xyz_arr = []

    # Timing and loop control
    target_end_time = datetime(*params.get('target_end_time'))

    iteration = 0
    while datetime.now() < target_end_time:
        iteration += 1
        print(f"\nStarting iteration {iteration} at {datetime.now().strftime('%H:%M:%S')}")

        # ----- XYZ Optimization -----
        data_xy, DM = scan_area(params, DM) 
        best_xy = data_xy.get('best_xy_loc')

        params['scan_center'] = (best_xy[0], best_xy[1])

        data_z, DM = scan_depth(params, DM)
        best_z = data_z.get('best_z_loc')
        
        params['scan_z_midpoint'] = best_z
        optimized_xyz = [best_xy[0], best_xy[1], best_z]
        xyz_positions.append(optimized_xyz)

        print(f"Optimized XYZ position: {optimized_xyz}")

        # Set optimized position
        gm.set_ao0(best_xy[0])
        gm.set_ao1(best_xy[1])

        # ----- RF Sweep -----
        freq, normalized, resonance = perform_RF_sweep(params, gm, apd, sg)
        
        freq_arr.append(freq)
        normalized_arr.append(normalized)
        resonance_arr.append(resonance)
        optimized_xyz_arr.append(optimized_xyz)
        
        timestamps.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # Prepare final combined data
    data = {
        'rf_sweep_results': rf_sweep_results,
        'freq_arr': freq_arr,
        'normalized_arr':normalized_arr,
        'resonance_arr': resonance_arr,
        'optimized_xyz_arr': optimized_xyz_arr,
        'xyz_positions': xyz_positions,
        'timestamps': timestamps,
        'additional_info': 'Combined XYZ optimization and RF sweeps',
    }

    return data, DM


def Combined_XYZ_in_RF_sweep(params, DM):
    
    gm = DM.devices.get("daq_ao")
    apd = DM.devices.get("apd")
    sg = DM.devices.get('RFSignalGenerator')
    
    start = params.get("start")
    stop = params.get("stop")
    stepsize = params.get("stepsize")
    amp = params.get("amplitude")
    N = params.get("repetition")
    count_time = params.get("count_time")

    sg.set_amplitude(amp)
    freq = np.linspace(start, stop, int((stop-start)/stepsize)+1)
    contrast_sum = np.zeros(len(freq))

    last_xyz_time = time.time()  # Track time for periodic XYZ scan
    optimized_xyz = None
    for n in range(N):
        print(f'RF Sweep repetition {n+1}/{N}')
        contrast = np.zeros(len(freq))

        for i, f in enumerate(freq):
            # Check if 10 seconds have passed for XYZ scan
            current_time = time.time()
            if current_time - last_xyz_time >= count_time:
                # Perform XYZ scan and update positions
                print(f" {count_time} seconds passed, performing XYZ scan at frequency {f} Hz")
                data_xy, DM = scan_area(params, DM)
                best_xy = data_xy.get('best_xy_loc')

                params['scan_center'] = (best_xy[0], best_xy[1])

                data_z, DM = scan_depth(params, DM)
                best_z = data_z.get('best_z_loc')

                params['scan_z_midpoint'] = best_z
                optimized_xyz = [best_xy[0], best_xy[1], best_z]

                print(f"Optimized XYZ position: {optimized_xyz}")

                # Set optimized position
                gm.set_ao0(best_xy[0])
                gm.set_ao1(best_xy[1])

                last_xyz_time = time.time()  # Update last XYZ scan time

            # Continue the RF sweep measurement
            apd_counts_off = apd.GetCountRate()
            
            sg.set_frequency(f)
            sg.switch_output(1)
            time.sleep(0.2)
            apd_counts_on = apd.GetCountRate()
            sg.switch_output(0)

            contrast[i] = apd_counts_on / apd_counts_off
        
        print(apd_counts_off)
        contrast_sum += contrast

    normalized = contrast_sum / N
    resonance_idx = np.argmin(normalized)
    resonance = freq[resonance_idx]

    print(f"Found resonance at frequency {resonance} Hz")
    print(f"Last optimized position {optimized_xyz}")
    
    data = {
        'repetition': N,
        'freq_range': freq,
        'normalized':normalized,
        'resonance': resonance,
        'optimized_xyz': optimized_xyz,
        'additional_info': 'Combined XYZ optimization and RF sweeps',
    }
    
    return data, DM





 

    
        
        