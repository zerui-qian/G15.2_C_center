# -*- coding: utf-8 -*-
"""
Created on Thu Nov 7 2024

@program: Measurement Controller
@functionality: This script allows to start various measurements.
"""
import sys
import os
sys.path.append(os.path.abspath(r'Devices'))
sys.path.append(os.path.abspath(r'Logging'))
sys.path.append(os.path.abspath(r'Measurements'))
import save
import measurements_spectrum as spectrum
import APDscanAttocube
from DeviceManager import *


# Configuration Section
measure_dummyAPDscan = 0
measure_APDscan = 0
measure_PLE = 0
measure_spectrum = 0
measure_APDScanAttocube = 1

general_params = {
    'sample_code': '23-09-2024-hBN',
    'chip': 2,
    'flake': 23,
    'excitation_power (mW)': 2.5,
    'excitation_wavelength': 520,
    'temperature': 4,
    'setup': 'BC5',
    'flake thickness (nm)': "?",
    }

# Parameters for each measurement type


APD_SCAN_ATTOCUBE_PARAMS = {
    "measurement": "APD_scan_attocube",
    "x_step": 1,
    "y_step": 1,
    "x_number": int(150),
    "y_number": int(150),
    "x_start": 0,
    "y_start": 0,    
    "stop_counts": 100e4,
    "single_direction": True,
    "live_plot": True
}


SPECTRUM_PARAMS = {
    "measurement": "spectrum",
    "integration_time": 1e-8
}




def main(DM):
    # Run the selected measurement
    log = general_params.copy()
        
    if measure_spectrum:
        print("Starting spectrum measurement")
        data = spectrum.spectrum(SPECTRUM_PARAMS, location='G15')
        log.update(SPECTRUM_PARAMS)
        
    elif measure_APDScanAttocube:
        print("Starting Attocube APD scan")
        # DM.connect_devices_for_measurement("APDscan")
        # daq = DM.get("daq_ao")
#        if (daq.ao0 == None) or (daq.ao1 == None):
#            daq.ao0 = 0
#            daq.ao1 = 0
        print(f"DeviceManager ID in main: {id(DM)}")

        #data, DM = APDscanAttocube.scan_area(APD_SCAN_ATTOCUBE_PARAMS, DM)
        data = APDscanAttocube.scan_area(APD_SCAN_ATTOCUBE_PARAMS)
        log.update(APD_SCAN_ATTOCUBE_PARAMS)

        
    else:
        print("Unknown measurement type")

    if data != None:
        save.save_measurement(data, log)
    print("Measurement complete.")
    return DM

if __name__ == "__main__":
    main(DM)
        