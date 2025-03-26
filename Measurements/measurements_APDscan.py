# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 20:13:52 2024

@author: QPG
"""

import numpy as np
import time
import sys
import os
sys.path.append(os.path.abspath(r'F:/Users/QPG/Documents/zerui_g15/C-hBN_new/Devices'))
import DeviceManager
from tqdm import tqdm

# Experiment parameters
wait_time = 0.2  # Wait time in seconds

def scan_area(params, DM):
    """General scan function for both APD_map and antidrift.

    Args:
        scan_center (tuple): Center coordinates of the scan area (x, y).
        x_step (float): Step size in the x-direction.
        y_step (float): Step size in the y-direction.
        x_number (int): Number of steps in the x-direction.
        y_number (int): Number of steps in the y-direction.
        antidrift (bool): If True, perform alignment to maximize brightness after each row.

    Returns:
        dict: A dictionary containing locations, PC0, PC1, and metadata.
    """
    scan_center = params.get("scan_center")
    x_step = params.get("x_step")
    y_step = params.get("y_step")
    x_number = params.get("x_number")
    y_number = params.get("y_number")
    antidrift = params.get("antidrift")
    
    if params.get("stop_scan") != None:
        stop = params.get("stop_scan")
        stop_counts = params.get("stop_counts")
    else:
        stop = False
        stop_counts = 0
        
    gm = DM.devices.get("daq_ao")
    apd = DM.devices.get("apd")
    
    # Calculate starting location based on the center and scan range
    start_x = scan_center[0] - x_number / 2 * x_step
    start_y = scan_center[1] - y_number / 2 * y_step

    locations, apd_counts = [], []
    max_counts = 0

    for i in tqdm(range(y_number)):
        for j in range(x_number):
            # Determine scan direction based on row for serpentine pattern
            loc_x = start_x + x_step * (j if i % 2 == 0 else (x_number - j - 1))
            loc_y = start_y + y_step * i
            gm.set_ao0(loc_x)
            gm.set_ao1(loc_y)
            locations.append([loc_x, loc_y])

            time.sleep(wait_time)
            apd_counts.append(apd.GetCountRate())
            print(apd_counts[-1])
            max_counts = max(max_counts, apd_counts[-1])


            # Display progress at the beginning of each row
            # if j == 0:
            #     print(f"Progress: {i / y_number * 100:.2f}% at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            if stop and (apd_counts[-1] > stop_counts):
                break
        print("Maximum counts so far: ", max_counts)
        if stop and (apd_counts[-1] > stop_counts):
            break
    max_index = np.argmax(apd_counts)
    best_loc = locations[max_index]       
        
    # If antidrift is enabled, align to maximum brightness after each row
    if antidrift and (not stop):
        gm.set_ao0(best_loc[0])
        gm.set_ao1(best_loc[1])

    # Prepare data dictionary to be saved
    data = {
        'locations': np.array(locations),
        'apd_counts': np.array(apd_counts),
        'scan_center': scan_center,
        'x_step': x_step,
        'y_step': y_step,
        'x_number': x_number,
        'y_number': y_number,
        'best_xy_loc': best_loc,
        'antidrift': antidrift,
        'wait_time': wait_time,
        'additional_info': 'Include any other relevant metadata here',
    }
    
    print("Maximum signal at ", locations[np.argmax(apd_counts)])

    return data, DM

def scan_depth(params, DM):
    """General scan function for piezo-controlled z-stage.

    Args:
        scan_midpoint (float): Midpoint of the scanning line.
        z_step (float): Step size in the z-direction.
        z_number (int): Number of steps in the z-direction.
        optimize_depth (bool): If True, finding the depth with maximum counts.

    Returns:
        dict: A dictionary containing locations, PC0, PC1, and metadata.
    """
    scan_z_midpoint = params.get("scan_z_midpoint")
    z_step = params.get("z_step")
    z_number = params.get("z_number")
    
    antidrift= params.get("antidrift")
    gm = DM.devices.get("daq_ao")
    apd = DM.devices.get("apd")
    
    
    start_z = scan_z_midpoint - z_number / 2 * z_step
    
    locations, apd_counts = [], []
    
    for i in tqdm(range(z_number)):
        loc_z = start_z + z_step * i
        gm.set_ao2(loc_z)
        locations.append(loc_z)
        
        time.sleep(wait_time)
        apd_counts.append(apd.GetCountRate())
        print(apd_counts[-1])
    
    total_counts = np.array(apd_counts)
    max_index = np.argmax(total_counts)     
    best_loc = locations[max_index]
    
    if antidrift:
        gm.set_ao2(best_loc)
            
    # Prepare data dictionary to be saved
    data = {
        'locations': np.array(locations),
        'apd_counts': np.array(apd_counts),
        'scan_z_midpoint': scan_z_midpoint,
        'z_step': z_step,
        'z_number': z_number,
        'best_z_loc': best_loc,
        'antidrift': antidrift,
        'wait_time': wait_time,
        'additional_info': 'Include any other relevant metadata here',
    }
    
    print("Maximum signal at ", locations[np.argmax(apd_counts)])

    return data, DM

    def dummy_scan_galvanic_mirror(params):
        """
        Perform a quick, low-resolution dummy scan of the galvanic mirror area
        to visually check the laser beam position. No data is recorded.
        
        Args:
            scan_center (tuple): Center coordinates of the scan area (x, y).
            full_x_step (float): Full scan step size in the x-direction.
            full_y_step (float): Full scan step size in the y-direction.
            x_number (int): Number of steps in the x-direction for full scan.
            y_number (int): Number of steps in the y-direction for full scan.
        
        Returns:
            None
        """
        scan_center = params.get("scan_center")
        x_step = params.get("x_step")
        y_step = params.get("y_step")
        x_number = params.get("x_number")
        y_number = params.get("y_number")
        
        DM = DeviceManager.DeviceManager()
        DM.connect_devices_for_measurement("APDscan")
        
        gm = DM.devices.get("daq_ao")
        
        # Set a larger step size to reduce resolution and scan time
        dummy_x_step = x_step * 10
        dummy_y_step = y_step * 10
        dummy_x_number = max(1, x_number // 10)  # Ensure at least one step
        dummy_y_number = max(1, y_number // 10)  # Ensure at least one step
    
        # Calculate starting position
        start_x = scan_center[0] - dummy_x_number / 2 * dummy_x_step
        start_y = scan_center[1] - dummy_y_number / 2 * dummy_y_step
    
        # Perform the dummy scan
        print("Starting dummy scan. Watch the laser beam to confirm the scan area.")
        for i in range(dummy_y_number):
            for j in range(dummy_x_number):
                loc_x = start_x + dummy_x_step * j
                loc_y = start_y + dummy_y_step * i
                gm.set_ao0(loc_x)
                gm.set_ao1(loc_y)
    
                time.sleep(0.05)  # Short wait time to quickly move across the area
