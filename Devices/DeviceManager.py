# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 20:28:38 2024

@author: Johannes Eberle
@functionality: Connect to any measurement device and store it as an object.
"""
# import Device_ANC350
# import Device_DAQ
# import Device_Msquared
# import Device_picoharp
# import Device_piezoStage
# import Device_powermeter
# import Device_tempController
# import Device_daq_counter
# import Device_daq_ao
# import Device_RF_signal_generator
# import Device_piezoController


# from HP4142B import *
# from NIDAQ import *
# from ELL14 import *
import piezoController
import picoharp
import sys
import Pyro4
sys.path.append(r'F:/Users/QPG/Documents\zerui_g15\C-hBN\base\experiment_base\zq_drivers\pyro_nw')
from nameserver_client import nameserver as ns
from colorama import Fore, Back, Style

Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.REQUIRE_EXPOSE = False
Pyro4.config.PICKLE_PROTOCOL_VERSION = 4   #added on 24-02-2022

class DeviceManager:
    _instance = None  # Class-level variable to store the singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DeviceManager, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not self.__initialized:
            self.devices = {}
            self.__initialized = True
    
    # def connect_device(self, device_name, device_class, *args, **kwargs):
    #     """Connect a single device if not already connected."""
    #     if device_name not in self.devices:
    #         try:
    #             device = device_class(*args, **kwargs)
    #             self.devices[device_name] = device
    #             print(f"{device_name} connected.")
    #         except Exception as e:
    #             print(f"Failed to connect {device_name}: {e}")
    
    
    
    def get(self,deviceName):
        # if deviceName == "apd":
        #     if self.devices.get("picoharp") != None:
        #         return self.devices.get("picoharp")
#            else:
#                return self.devices.get("daq_counter")
        return self.devices[deviceName]
    
    def connect_devices_for_measurement(self, objectId, nameserver=ns, exile_id=None, uri=None):
        try:
            if exile_id is not None:
                uri = 'PYRO:' + exile_id + '@phd-exile-phys.ethz.ch:' + str(9091)
            elif uri is None:
                uri = nameserver.lookup(objectId)
                # if objectId == "piezoController":
                #     self.connect_device("pz", piezoController.Controller)
                # elif objectId == "picoharp":
                #     self.connect_device("picoharp", picoharp.picoharp)
                #     self.devices["picoharp"].Calibrate()
            proxy = Pyro4.Proxy(uri)
            proxy._pyroBind()
            print(Fore.GREEN + Style.BRIGHT + "Connection success: " + objectId + Fore.RESET)
            return proxy
        except:
            print(Fore.RED + Style.BRIGHT + "Connection failure: " + objectId + Fore.RESET)
            return None

    # def connect_devices_for_measurement(self, measurement,apd_device="picoharp",
    #                                     sampling_rate=3e5, acq_time=0.05):
    #     """Connect devices based on the measurement type."""
    #     if measurement in ["APDscan", "timeAPD"]:
    #         self.connect_device("ANC350", Device_ANC350.ANC350)
    #         #self.connect_device("DAQ", Device_DAQ.DAQ)
    #         #self.connect_device("daq_ao", Device_daq_ao.daq_ao)
    #         self.connect_device("pz", piezoController.Controller)
    #         if apd_device == "picoharp":
    #             self.connect_device("apd", picoharp.picoharp)
    #             self.devices["apd"].Calibrate()
            # else:
            #     self.connect_device("apd", Device_daq_counter.daq_counter,
            #                         sampling_rate=sampling_rate,
            #                         acq_time=acq_time)
        # elif measurement in ["RF_sweep"]:
        #         self.connect_device("RFSignalGenerator", Device_RF_signal_generator.RFSignalGenerator)
        #         self.connect_device("daq_ao", Device_daq_ao.daq_ao)
        #         if apd_device == "picoharp":
        #             self.connect_device("apd", Device_picoharp.picoharp)
        #         else:
        #             self.connect_device("apd", Device_daq_counter.daq_counter,
        #                                 sampling_rate=sampling_rate, acq_time=acq_time)
        # elif measurement == "PLE":
        #     self.connect_device("ANC350", Device_ANC350.ANC350)
        #     #self.connect_device("DAQ", Device_DAQ.DAQ)
        #     self.connect_device("daq_ao", Device_daq_ao.daq_ao)
        #     self.connect_device("picoharp", Device_picoharp.picoharp)
        #     self.connect_device("Msquared", Device_Msquared.Msquared)
        #     self.connect_device("piezoStage", Device_piezoStage.piezoStage)
        #     self.connect_device("powermeter", Device_powermeter.powermeter)
        #     self.connect_device("tempController", Device_tempController.tempController)

        # elif measurement == "PLE_test":
        #     self.connect_device("Msquared", Device_Msquared.Msquared)
        #     self.connect_device("piezoStage", Device_piezoStage.piezoStage)
        #     self.connect_device("powermeter", Device_powermeter.powermeter)
        #     self.connect_device("tempController", Device_tempController.tempController)

    def disconnect_device(self, device_name):
        """Disconnect a specific device if it is connected."""
        if device_name in self.devices:
            try:
                self.devices[device_name].disconnect()
                print(f"{device_name} disconnected.")
                del self.devices[device_name]
            except Exception as e:
                print(f"Error disconnecting {device_name}: {e}")
    
    def disconnect_all(self):
        """Disconnect all connected devices."""
        for device_name in list(self.devices.keys()):
            self.disconnect_device(device_name)

DM = DeviceManager()
HP4142B       = DM.connect_devices_for_measurement('HP4142B_r')
WinSpec       = DM.connect_devices_for_measurement('WinSpec', exile_id = 'WinSpec')
# LightField_c    = connect('LightField', uri = 'PYRO:LightField@G15-Pylon.dhcp-int.phys.ethz.ch:63899')        
NIDAQ = DM.connect_devices_for_measurement("NIDAQ")
# ELL1_c = connect("ELL14")
# ELL2_c = connect("ELL14_2")
# ELL3_c = connect("ELL14_3")
pz = DM.connect_devices_for_measurement("piezoController")
ph = DM.connect_devices_for_measurement("picoharp")
ph.Calibrate()