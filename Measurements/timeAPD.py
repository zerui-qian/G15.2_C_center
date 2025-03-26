# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 15:49:46 2025

@author: QPG
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time  # To track elapsed time
import sys
sys.path.append(r'F:/Users/QPG/Documents/zerui_g15/C-hBN_new/Devices')
from Device_picoharp import *

ph = picoharp()
ph.Calibrate()

times = []  # Stores absolute time values
counts = []  # Stores count rate values
start_time = time.time()  # Reference start time

fig, ax = plt.subplots(figsize=(8, 4))
line, = ax.plot([], [], 'r-', label="Count Rate (Hz)")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Count Rate (Hz)")
ax.set_title("Live Count Rate Monitor")
ax.grid(True)

def update(frame):
    current_time = time.time() - start_time  # Elapsed time since start
    new_count = ph.GetCountRate()  

    # Append new values
    times.append(current_time)
    counts.append(new_count)
    line.set_data(times, counts)

    # Auto-rescale axes
    ax.relim()  # Recalculate limits based on new data
    ax.autoscale_view()  # Rescale the view to fit new limits

    return line,

ani = animation.FuncAnimation(fig, update, interval=100)
plt.show()