# -*- coding: utf-8 -*-
"""
Created on Thu Mar  6 18:19:43 2025

@author: QPG G8.1
"""
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  6 17:37:57 2025

@author: QPG G8.1
"""
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 16:14:38 2025

@author: QPG G8.1
"""

import nidaqmx
from nidaqmx.constants import Edge, AcquisitionType
import time
import sys

class daq_ao:
    def __init__(self, device='Dev1/'):
        self.device_name = device
        self._ao0 = None
        self._ao1 = None
        self._ao2 = None
        self.output_handle = sys.stdout
        
    @property
    def ao0(self):
        return self._ao0

    @property
    def ao1(self):
        return self._ao1

    def set_ao0(self, voltage):
        """Set voltage going to nf power setpoint. Takes 3.1 ms!."""
        with nidaqmx.Task() as vTask:
            vTask.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            vTask.write(voltage, auto_start=True)
            vTask.stop()
        self._ao0 = voltage


    def set_ao1(self, voltage):
        """Set voltage going to FPGA AI0. Takes 3.1 ms!."""
        with nidaqmx.Task() as vTask:
            vTask.ao_channels.add_ao_voltage_chan('Dev1/ao1')
            vTask.write(voltage, auto_start=True)
            vTask.stop()
        self._ao1 = voltage

    def set_ao2(self, voltage):
        """Set voltage going to FPGA AI0. Takes 3.1 ms!."""
        with nidaqmx.Task() as vTask:
            vTask.ao_channels.add_ao_voltage_chan('Dev1/ao2')
            vTask.write(voltage, auto_start=True)
            vTask.stop() 
        self._ao2 = voltage
 
    def set_aoxy(self, voltage_0, voltage_1):
        self.set_ao0(voltage_0)
        self.set_ao1(voltage_1)

        
    def smooth_set_ao0(self, target_value, step_size=0.01, delay=0.05):
        """
        Written by Johannes on December 15, 2024
        Smoothly sets ao0 from its current value to the target value.
        
        Parameters:
            target_value (float): The value to set ao0 to.
            step_size (float): The increment size for each step.
            delay (float): The time (in seconds) to wait between each step.
        """
        current_value = self.ao0
        direction = 1 if target_value > current_value else -1
        total_steps = int(abs(target_value - current_value) / step_size)

        for _ in range(total_steps):
            current_value += direction * step_size
            self.set_ao0(current_value)
            time.sleep(delay)

        # Ensure the final value is set accurately
        self.set_ao0(target_value)
        
    def smooth_set_ao1(self, target_value, step_size=0.01, delay=0.05):
        """
        Written by Johannes on December 15, 2024
        Smoothly sets ao1 from its current value to the target value.
        
        Parameters:
            target_value (float): The value to set ao0 to.
            step_size (float): The increment size for each step.
            delay (float): The time (in seconds) to wait between each step.
        """
        current_value = self.ao1
        direction = 1 if target_value > current_value else -1
        total_steps = int(abs(target_value - current_value) / step_size)

        for _ in range(total_steps):
            current_value += direction * step_size
            self.set_ao1(current_value)
            time.sleep(delay)

        # Ensure the final value is set accurately
        self.set_ao1(target_value)    


    def close(self):
        '''Close method that does nothing for now.'''
        pass
    
  
        
