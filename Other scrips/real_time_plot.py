# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 16:56:27 2025

@author: QPG G8.1
"""

import matplotlib.pyplot as plt
import time
import os
import sys
# Determine the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
devices_dir = os.path.abspath(os.path.join(current_dir, "..", "Devices"))
sys.path.append(devices_dir)
import Device_daq_counter

def real_time_plot(apd):
    plt.ion()  # Enable interactive mode
    fig, ax = plt.subplots()
    
    time_vals = []
    count_vals = []
    update_count = 0
    start_time = time.time()
    
    while True:
        # Get the current count rate from the device
        count_rate = apd.GetCountRate()
        current_time = time.time() - start_time
        
        # Append new data
        time_vals.append(current_time)
        count_vals.append(count_rate)
        
        # Determine the cutoff time: only data within the last 180 seconds (3 minutes)
        cutoff = current_time - 180
        
        # Filter data: since time_vals is sorted, use list comprehension to select recent points
        plot_time = [t for t in time_vals if t >= cutoff]
        plot_counts = [count_vals[i] for i, t in enumerate(time_vals) if t >= cutoff]
        
        # Clear and update the plot with only the last 3 minutes of data
        ax.clear()
        ax.plot(plot_time, plot_counts, label="Count Rate", color='b')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Count Rate (counts/s)')
        ax.set_title('Real-Time Photon Detection (Last 3 Minutes)')
        ax.legend()
        
        plt.draw()
        plt.pause(0.1)
        
        update_count += 1
        if update_count > 70000:  # Example condition to stop after many updates
            break
    
    plt.ioff()  # Disable interactive mode
    plt.show()
    
if __name__ == "__main__":
    apd = Device_daq_counter.daq_counter(sampling_rate=1e3, acq_time=0.1)
    real_time_plot(apd)