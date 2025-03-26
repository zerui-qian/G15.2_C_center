# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 18:20:26 2025

@author: Nikki Braganza
"""

import numpy as np
import time
import sys
import os
sys.path.append(os.path.abspath(r'D:\Users\QPG G8.1\Documents\Python Scripts\Johannes github code\Measurements'))
import DeviceManager
from tqdm import tqdm
import time
from measurements_APDscan import *
from datetime import datetime

def XYZ_APDscan(params,DM):
    start = time.time()
    time_vals = []
    count_vals = []
    xyz_optimun_vals = []
    target_end_time = datetime(*params.get('target_end_time'))
    apd = DM.devices.get("apd")
    while datetime.now() < target_end_time:
        
        timestamp = time.time()
        dt_object = datetime.fromtimestamp(timestamp)
        # Extract just the time
        current_time = dt_object.strftime("%H:%M:%S")
        print(current_time)
        
        while time.time()-timestamp < params.get('count_time'):
            
            count_rate = apd.GetCountRate()

            time_vals.append(time.time() - start)
            count_vals.append(count_rate)
            
        data, DM = scan_area(params,DM) 
        params['scan_center'] = (data.get('best_xy_loc')[0] ,data.get('best_xy_loc')[1])
        
        data_z, DM = scan_depth(params, DM)
        
        xyz_optimun_vals.append([data.get('best_xy_loc')[0],data.get('best_xy_loc')[1], 
                                 data_z.get('best_z_loc')])
        
        
        params['scan_z_midpoint'] = data_z.get('best_z_loc')
        
    data = {
        'time_vals': np.array(time_vals),
        'count_vals': np.array(count_vals),
        'xyz_optimun_vals': np.array(xyz_optimun_vals),
        'additional_info': 'Include any other relevant metadata here',
    }
    
    print("Maximum signal at ", xyz_optimun_vals[-1])

    return data, DM
        
        
        
    
        
        