# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 22:05:04 2024

@author: Johannes Eberle
@functionality: PLE
"""

import time
import numpy as np
import csv
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(r'C:\Users\QPG\Documents\Python Scripts\johannes'))
sys.path.append(os.path.abspath(r'C:\Users\QPG\Documents\Python Scripts\leliu'))
sys.path.append(os.path.abspath(r'C:\Users\QPG\Documents\Python Scripts\johannes\Control code\Devices'))
sys.path.append(os.path.abspath(r'C:\Users\QPG\Documents\Python Scripts\johannes\Control code\Other scripts'))
import tempControl
import DeviceManager


def PLE(params, DM):
    
    start_wv = params.get("start_wv")
    end_wv = params.get("end_wv")
    stepsize = params.get("stepsize")
    wav = np.arange(start_wv, end_wv, stepsize)
    averages = params.get("count_averages")
    test = params.get("test")
    max_power= params.get("power")
    opt_power = params.get("optimize_power")
    fast_opt = params.get("fast_temperature_optimization")
    fast_opt = params.get("fast_temperature_optimization")

    if not test:
        ph = DM.get("picoharp")
    laser = DM.get("Msquared")
    pm = DM.get("powermeter")
    stage = DM.get("piezoStage")
    oc = DM.get("tempController")
    
    # Define the filename for the CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Base folder path
    base_folder = 'Z:\\Projects\\Defects for QTM\\Raw data\\'
    
    # Get the current date in YYYY-MM-DD format
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Combine base folder and current date to create the target folder path
    folder = os.path.join(base_folder, current_date) + '\\'
    
    # Check if the folder exists, and if not, create it
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Folder created: {folder}")
    else:
        print(f"Folder already exists: {folder}")    
    
    filename = f'wavelengths_{timestamp}.csv'

    filename_temperatureLog = f'temperatureLog_{timestamp}.csv'

    # Create and initialize the CSV file with column titles
    with open(folder + filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow([
            "Set wavelength (nm)", "Measured wavelength (nm)", "Power (mW)", 
            "Iteration Time (s)", "Temperature (Celsius)", "Successes", 
            "Laser tunings", "Tuning problems", "APD counts"
        ])
    

    print("Start wavelength: ", start_wv, " nm")
    
    for i in range(len(wav)):
        stage.move_to(750)
        print("Setting laser to ", start_wv + i * stepsize, " nm")
        start_time = time.time()  # Start the timer
        cont = False
        for k in range(0, 3):
            cont = False
            try:
                laser.fine_tune_wavelength((start_wv + i * stepsize) * 1e-9)
            except:
                pass
            
        
        if i == wav[0]:
            fast_opt = False
        else:
            fast_opt = True
        temp, success, laser_tunings, tuning_problems = tempControl.temp_opt(
            oc, pm, laser, start_wv + i * stepsize, max_power=max_power, 
            opt_power=opt_power, fast_opt=fast_opt, 
            csv_filename=folder + filename_temperatureLog
        )
        
        measured_wl = laser.get_fine_wavelength()
        
        end_time = time.time()  # End the timer
        iteration_time = end_time - start_time  # Calculate the elapsed time
        
        power_beforeMeasurement = pm.get_power() * 1e3
        stage.move_to(250)
        time.sleep(0.2)
        counts = 0
        if not test:
            for j in range(0, averages):
                #counts += (ph.GetCountRate(chan=0) + ph.GetCountRate(chan=1))
                counts += ph.GetCountRate(chan=0)
                time.sleep(0.2)
            counts /= averages
            print(counts)
        
        with open(folder + filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Write the data row
            writer.writerow([
                start_wv + i * stepsize, measured_wl, power_beforeMeasurement, 
                iteration_time, temp, success, laser_tunings, tuning_problems, counts
            ])
    
    # Read the CSV file back into numpy arrays and create a dictionary
    data_dict = {}
    with open(folder + filename, mode='r') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Get the header row
        data = np.array(list(reader), dtype=float)  # Read the rest as numpy array
        
        # Create a dictionary with column names as keys and data as numpy arrays
        for col_index, header in enumerate(headers):
            data_dict[header] = data[:, col_index]
    
    return data_dict

