# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 14:37:12 2025

@author: Johannes Eberle and Nikki Braganza
"""
import  pyvisa as visa

# rm = visa.ResourceManager()
# print(rm.list_resources()) # shows list of devices
# dev = rm.open_resource('GPIB0::19::INSTR') # connection to E8257D signal generator
# print(dev.query('*IDN?')) # make sure you are connected to correct device

# dev.write('FREQ 5 GHz')  # set the frequency

# current_frequency = dev.query('FREQ?') # querying the current frequency
# print(f"Current frequency: {current_frequency}")

# dev.close() # Close the connection to the device

# import pyvisa as visa

class RFSignalGenerator:
    def __init__(self, visa_address='GPIB0::19::INSTR'):
        """
        Initialize the connection to the E8257D Signal Generator.
        
        :param visa_address: The VISA address of the signal generator (e.g., 'GPIB0::19::INSTR').
        """
        self.rm = visa.ResourceManager()  # Resource Manager for PyVISA
        self.dev = self.rm.open_resource(visa_address)  # Open the device connection
        print(f"Connected to: {self.dev.query('*IDN?')}")  # Print the device ID for confirmation

    def set_frequency(self, frequency):
        """
        Set the frequency of the signal generator.
        
        :param frequency: The frequency to set (e.g., '5 GHz', '1 MHz').
        """
        self.dev.write(f'FREQ {frequency} GHz')  # Set the frequency
        print(f"Frequency set to: {frequency}")
    
    def set_amplitude(self, amplitude):
        """
        Set the amplitude of the signal generator.
        
        :param amplitude: The amplitude to set (e.g., '5 GHz', '1 MHz').
        """
        self.dev.write(f'POW {amplitude} dBm')  # Set the power 
        print(f"Amplitude set to: {amplitude}")

    def get_frequency(self):
        """
        Query the current frequency of the signal generator.
        
        :return: The current frequency as a string.
        """
        current_frequency = self.dev.query('FREQ?')  # Query the current frequency
        return current_frequency.strip()  # Strip any trailing whitespace
    
    def switch_output(self, command):
        if command == 0:
            self.dev.write('OUTP OFF')
             
        else:
            self.dev.write('OUTP ON')
             
        

    def disconnect(self):
        """
        Close the connection to the signal generator.
        """
        self.dev.close()
        

# Example usage:
if __name__ == '__main__':
    # Create an object of the E8257DSignalGenerator class with the VISA address of the instrument
    signal_generator = RFSignalGenerator()

    # Set the frequency to 5 GHz
    signal_generator.set_frequency('5 GHz')

    # Get the current frequency
    current_freq = signal_generator.get_frequency()
    print(f"Current frequency: {current_freq}")

    # Close the connection
    signal_generator.disconnect()
