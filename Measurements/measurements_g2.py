# -*- coding: utf-8 -*-
"""
Created on Tue Mar 25 16:05:59 2025

@author: QPG
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 10:40:17 2024

@author: QPG
"""
import time
import numpy as np
from datetime import datetime
from measurements_APDscan import scan_area, scan_depth
import os
import sys
sys.path.append(os.path.abspath(r'D:\Users\QPG G8.1\Documents\Python Scripts\Johannes github code\Devices'))
sys.path.append(os.path.abspath(r'D:\Users\QPG G8.1\Documents\Python Scripts\Johannes github code\Measurements'))
import DeviceManager


def g2_drift_correction(params, DM):
    
    gm = DM.devices.get("daq_ao")
    ph = DM.devices.get("apd")
    
    ph.opendefaults()
    ph.ClearHistMem()
    
    defect_position = params.get("defect_position")
    gm.set_ao0(defect_position[0])
    gm.set_ao1(defect_position[1])

    count_time = params.get("count_time")
    optimized_xyz = None
    count_arr = []

    ph.StartMeas(tacq=int(65530e3))
    iteration = 0
    
    while True:
    
        # Perform XYZ scan and update positions            
        data_z, DM = scan_depth(params, DM)
        best_z = data_z.get('best_z_loc')
            
        data_xy, DM = scan_area(params, DM)
        best_xy = data_xy.get('best_xy_loc')

        optimized_xyz = [best_xy[0], best_xy[1], best_z]
        print(f"Optimized XYZ position: {optimized_xyz}")
        
        params["scan_center"] = best_xy
        params["scan_z_midpoint"] = best_z
            
        count = ph.GetCountRate(chan=0)+ph.GetCountRate(chan=1)
        count_arr.append(count)
        print(count)
        
        if (count>400) and (ph.GetElapsedMeasTime()<65000e3):
            print(count, iteration) 
        else:
            hist = ph.GetHistogram()
            break
        
        print('elapse_time=%d s'%ph.GetElapsedMeasTime())
        print('total_count=%d '%np.sum(ph.GetHistogram()))
        
        iteration += 1
        time.sleep(count_time)
        
    data = {
        'histogram': hist,
        'iteration': iteration,
        'count_arr': np.array(count_arr)
     }

    return data, DM



# i=1
# anti_c=0
# while i==1:
    
#     count=0
    
#     if anti_c%1==0:
        
#         antidrift(address)
        
#         if anti_c !=0:
            
#             hist = ph.GetHistogram()
#             dataframe_hist = pd.DataFrame(hist)
#             dataframe_hist.to_csv(address+r'\ph_hist_'+name+time.strftime("%y-%m-%d-%H-%M-%S",time.localtime())+'.csv', index=False, sep=',')
   
#     anti_c=anti_c+1
    
#     for j in range(10):
        
#         count=count+ph.GetCountRate(chan=0)+ph.GetCountRate(chan=1)
#         time.sleep(0.2)
        
#     count=int(count/10)
    
    
#     if (count>400) and (ph.GetElapsedMeasTime()<65000e3):
        
#         print(count) 
        
#         with open(address+r'\CPS_with_time'+name+'.txt','a') as f:
            
#             f.write('%s\t' % (time.strftime("%y-%m-%d-%H-%M-%S",time.localtime())))
#             f.write('\t')     
#             f.write('%d\t' % (count))
#             f.write('\t')
#             f.write('\n') 
            
#         f.close
                
#     else:
        
#         hist = ph.GetHistogram()
#         dataframe_hist = pd.DataFrame(hist)
#         dataframe_hist.to_csv(address+r'\ph_hist_'+name+time.strftime("%y-%m-%d-%H-%M-%S",time.localtime())+'.csv', index=False, sep=',')
#         sys.exit()
        
    
#     print('elapse_time=%d s'%ph.GetElapsedMeasTime())
#     print('total_count=%d '%np.sum(ph.GetHistogram()))
#     time.sleep(600)
