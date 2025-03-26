# -*- coding: utf-8 -*-
"""
Created on Thu Dec  12 10:52:52 2024

@author: Johannes Eberle
"""

import numpy as np
import time
import sys
import os
sys.path.append(os.path.abspath(r'F:/Users/QPG/Documents/zerui_g15/C-hBN_new/Devices'))
from DeviceManager import *
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style


# Experiment parameters
#wait_time = 0.1  # Wait time in seconds
#wait_time = 0.15  # Wait time in seconds
wait_time = 0.05

def scan_area(params):
    """General scan function for both APD_map and antidrift.

    Args:
        x_step (float): Step size in the x-direcon.
        y_step (float): Step size in the y-direction.
        x_number (int): Number of steps in the x-direction.
        y_number (int): Number of steps in the y-direction.

    Returns:
        dict: A dictionary containing locations, PC0, PC1, and metadata.
    """
    x_step = params.get("x_step")
    y_step = params.get("y_step")
    x_number = params.get("x_number")
    y_number = params.get("y_number")
    x_start = params.get("x_start")
    y_start = params.get("y_start")
    stop_counts = params.get("stop_counts")
    single_direction = params.get("single_direction")
    live_plot = params.get("live_plot")
    
    print(params)

    

    print(f"DeviceManager ID in scan_area: {id(DM)}")
    
    # Calculate starting location based on the center and scan range
    start_x = x_start
    start_y = y_start
#    DAQ.set_ao0(ao0)
#    DAQ.set_ao1(ao1)

    
#    print("DAQ ao0 initial value: ", DAQ.ao0)
#    print("DAQ ao1 initial value: ", DAQ.ao1)
#    print(DAQ)
#    
#    if (DAQ.ao0 != None) and (DAQ.ao1 != None):
#        DAQ.smooth_set_ao0(x_start)
#        DAQ.smooth_set_ao1(y_start)
#    else:
#        raise Exception("Attocube scanner could not be set!")

    locations, counts = [], []
    
    if live_plot == True:
        # Initialize data storage
        image_data = np.zeros((y_number, x_number))  # 2D array for pixel representation
    
        # Initialize figure
        fig, ax = plt.subplots()
        img = ax.imshow(image_data, cmap="magma", origin="lower", extent=[x_start, x_start + x_step * x_number, y_start, y_start + y_step * y_number])
        cbar = fig.colorbar(img, ax=ax)  # Add colorbar
        cbar.set_label("APD Counts")
    
        ax.set_title("Live APD Scan")
        ax.set_xlabel("SCx (V)")
        ax.set_ylabel("SCy (V)")
        ax.set_xlim(x_start, x_start + x_step * x_number)
        ax.set_ylim(y_start, y_start + y_step * y_number)
        plt.ion()  # Turn on interactive mode
    
    min_counts, max_counts = np.inf, 0  # Track min/max APD values dynamically

    for i in tqdm(range(y_number)):
        for j in range(x_number):
            # Determine scan direction based on row for serpentine pattern
            if single_direction: x_idx = j
            else: x_idx = j if i % 2 == 0 else (x_number - j - 1)
            
            loc_x = x_start + x_step * x_idx
            loc_y = y_start + y_step * i
            pz.set_SCx(loc_x)
            locations.append([loc_x, loc_y])
            time.sleep(wait_time)

            apd_counts = ph.GetCountRate()
            counts.append(apd_counts)
            max_counts = max(max_counts, apd_counts)
            
            if live_plot == False: print(apd_counts)
            else:
                image_data[i, x_idx] = apd_counts
                if apd_counts > 0:  # Ignore initial zeros
                    min_counts = min(min_counts, apd_counts)
                    
                img.set_data(image_data)
                img.set_clim(vmin=min_counts, vmax=max_counts)  # Update color scale
                cbar.update_normal(img)  # Update colorbar

                fig.canvas.draw_idle()  # Redraw figure
                plt.pause(0.001)  # Short pause to refresh
            
            if apd_counts >= stop_counts:
                print(pz.get_SCx(), pz.get_SCy())
                break
            
            if live_plot == False and j==0:
                # Display progress at the beginning of each row
                print(f"Progress: {i / y_number * 100:.2f}% at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("Maximum counts so far: ", max_counts)
        
        if apd_counts >= stop_counts: break
        pz.set_SCy(loc_y)
        
        # if live_plot == True:
        #     image_data[i, :] = counts[x_number * i : x_number * (i + 1)]
            
        #     if apd_counts > 0:  # Ignore initial zeros
        #         min_counts = min(min_counts, apd_counts)
                
        #     img.set_data(image_data)
        #     img.set_clim(vmin=min_counts, vmax=max_counts)  # Update color scale
        #     cbar.update_normal(img)  # Update colorbar

        #     fig.canvas.draw_idle()  # Redraw figure
        #     plt.pause(0.001)  # Short pause to refresh
        
    if live_plot == True:
        plt.ioff()  # Turn off interactive mode at the end
        plt.show()


    # Prepare data dictionary to be saved
    data = {
        'locations': np.array(locations),
        'apd_counts': np.array(counts),
        'x_step': x_step,
        'y_step': y_step,
        'x_number': x_number,
        'y_number': y_number,
        'wait_time': wait_time,
        'additional_info': 'Include any other relevant metadata here',
    }
#    DAQ.smooth_set_ao0(0)
#    DAQ.smooth_set_ao1(0)
    return data

    # def dummy_scan(params, DM):
    #     """
    #     Perform a quick, low-resolution dummy scan of the galvanic mirror area
    #     to visually check the laser beam position. No data is recorded.
        
    #     Args:
    #         scan_center (tuple): Center coordinates of the scan area (x, y).
    #         full_x_step (float): Full scan step size in the x-direction.
    #         full_y_step (float): Full scan step size in the y-direction.
    #         x_number (int): Number of steps in the x-direction for full scan.
    #         y_number (int): Number of steps in the y-direction for full scan.
        
    #     Returns:
    #         None
    #     """
    #     scan_center = params.get("scan_center")
    #     x_step = params.get("x_step")
    #     y_step = params.get("y_step")
    #     x_number = params.get("x_number")
    #     y_number = params.get("y_number")
        
    #     DM.connect_devices_for_measurement("APDscan")
        
    #     DAQ = DM.devices.get("DAQ")
        
    #     # Set a larger step size to reduce resolution and scan time
    #     dummy_x_step = x_step * 10
    #     dummy_y_step = y_step * 10
    #     dummy_x_number = max(1, x_number // 10)  # Ensure at least one step
    #     dummy_y_number = max(1, y_number // 10)  # Ensure at least one step
    
    #     # Calculate starting position
    #     start_x = scan_center[0] - dummy_x_number / 2 * dummy_x_step
    #     start_y = scan_center[1] - dummy_y_number / 2 * dummy_y_step
    
    #     if (DAQ.ao1 != None) and (DAQ.ao2 != None):
    #         DAQ.smooth_set_ao0(x_start)
    #         DAQ.smooth_set_ao1(y_start)
    #     else:
    #         print("Attocube scanner will be set non-smoothly")
        
    #     # Perform the dummy scan
    #     print("Starting dummy scan. Watch the laser beam to confirm the scan area.")
    #     for i in range(dummy_y_number):
    #         for j in range(dummy_x_number):
    #             loc_x = start_x + dummy_x_step * j
    #             loc_y = start_y + dummy_y_step * i
    #             DAQ.set_ao0(loc_x)
    #             DAQ.set_ao1(loc_y)
    
    #             time.sleep(0.05)  # Short wait time to quickly move across the area

    #     return DM