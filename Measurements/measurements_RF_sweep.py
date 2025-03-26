# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 15:19:03 2025

@author: Nikki Braganza 
"""
import numpy as np
import time
import sys
import os
sys.path.append(os.path.abspath(r'D:\Users\QPG G8.1\Documents\Python Scripts\Johannes github code\Devices'))
import DeviceManager



def RF_sweep(params, DM):
    
    defect_position = params.get("defect_position")
    print(type(defect_position))
    start = params.get("start")
    stop = params.get("stop")
    stepsize = params.get("stepsize")
    amp = params.get("amplitude")
    N = params.get("repetition")
    
    gm = DM.devices.get("daq_ao")
    apd = DM.devices.get("apd")
    sg = DM.devices.get('RFSignalGenerator')
    
    time.sleep(0.2)
    gm.set_ao0(defect_position[0])
    gm.set_ao1(defect_position[1])
    sg.set_amplitude(amp)
    
    freq = np.linspace(start, stop, int((stop-start)/stepsize)+1)
    sums = np.zeros(len(freq))
    apd_counts = np.zeros(len(freq))
    contrast = np.zeros(len(freq))
    
    # averaging
    for n in range(N):
        print(f'We are at the {n}-th')
        i=0
        for f in freq:
            time.sleep(0.2)
            apd_counts_off = apd.GetCountRate()
            sg.set_frequency(f)
            sg.switch_output(1)
            time.sleep(0.2)
            apd_counts_on = apd.GetCountRate()
            sg.switch_output(0)
            
            contrast[i] = apd_counts_on / apd_counts_off
            i = i+1
        sums = sums + contrast
         
        
    normalized = sums/N
    min_index = np.argmin(apd_counts)
    resonance = freq[min_index]      
    data = {
        'freq_range': freq,
        'resonance': resonance,
        'normalized': normalized,
        'additional_info': 'Include any other relevant metadata here',
    }
    
    print("Resonance signal at ", resonance)

    return data, DM
        
