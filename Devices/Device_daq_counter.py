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

class daq_counter:
    def __init__(self, device='Dev1/', channel='ctr0', sampling_rate=3e5, acq_time=0.05):
        '''Initialize the DAQCounter with device, channel, sampling rate, and acquisition time.'''
        self.device_name = device
        self.channel = channel
        self.sampling_rate = int(sampling_rate)
        self.acq_time = acq_time
        self.num_points = int(self.sampling_rate * self.acq_time)

        

    def get_one_ctrs(self):
        '''Read a single counter channel from the DAQ card.'''
        with nidaqmx.Task() as CtrTask1, nidaqmx.Task() as CtrTask2, nidaqmx.Task() as ClkTask:
            # Configure the counter task
            CtrTask1.ci_channels.add_ci_count_edges_chan(self.device_name + self.channel, edge=Edge.RISING)
            # Configure the clock task
            ClkTask.ai_channels.add_ai_voltage_chan(self.device_name + 'ai2')

            # Configure sample clock timing
            ClkTask.timing.cfg_samp_clk_timing(self.sampling_rate, samps_per_chan=self.num_points,
                                               sample_mode=AcquisitionType.FINITE, source='')
            CtrTask1.timing.cfg_samp_clk_timing(self.sampling_rate, samps_per_chan=self.num_points,
                                                 sample_mode=AcquisitionType.FINITE, source='/'+ self.device_name +'ai/SampleClock')

            # Start tasks
            CtrTask1.start()
            ClkTask.start()

            # Read counter values
            Cntr1 = CtrTask1.read(number_of_samples_per_channel=self.num_points, timeout=self.acq_time * 1.1)
            
            # Stop tasks
            ClkTask.stop()
            CtrTask1.stop()

        return Cntr1

    def GetCountRate(self):
        counts = self.get_one_ctrs()
        return counts[-1] / self.acq_time

    def close(self):
        '''Close method that does nothing for now.'''
        pass
    
  
        
