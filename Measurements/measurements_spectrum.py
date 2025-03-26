# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 22:06:49 2024

@author: Johannes Eberke
@functionality: Take the spectrum
"""

import time
import Pyro4


# Pyro4 configuration
Pyro4.config.SERIALIZER = 'serpent'
Pyro4.config.SERIALIZERS_ACCEPTED = {'serpent', 'json', 'marshal', 'pickle'}

# Connects to WinSpec in G13
################
def spectrum(params, location):
    e_time = params.get("integration_time")
    print('connect to ws')
    
    uri_map = {
        "G8": 'PYRO:WinSpec@phd-exile-phys.ethz.ch:9093',  # G8 spectrometer
        "G11": 'PYRO:WinSpec@phd-exile-phys.ethz.ch:9091',  # G11 spectrometer
        "G13": 'PYRO:WinSpec@G13-spectrometer.dhcp-int.phys.ethz.ch:9090', # G13 spectrometer
        "G15": 'PYRO:WinSpec@phd-exile-phys.ethz.ch:9091',  # G15 spectrometer
    }

    # Get the URI based on the location argument 
    uri = uri_map.get(location)
    
    ws = Pyro4.Proxy(uri)
    print(ws)
    ws.exposure_time=e_time
    nFrames = 1
    ws.num_frames = nFrames
    #    buf = ws.get_spectrum(wlen=True)
    # gratingDict = {1500: 1, 300: 2, 1200: 3}
    print('spect ok')
    ###########################
    
    time.sleep(0.5)
    
    buf = ws.get_spectrum(wlen=True)
    spec,w_array = buf    

    data = {
        'intensity': spec,
        'wavelength': w_array,
        'integration_time': e_time,
        'additional_info': 'Include any other relevant metadata here',
    }
    return data