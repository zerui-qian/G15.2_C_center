# -*- coding: utf-8 -*-
"""
Created on Thu Sep 6 10:58:02 2024

@author: Johannes Eberle
@functionality: This is the Thorlabs powermeter. In this code, we inherit from the Throlabs.PM160 class in pylablib with all the methods associated to it.

"""
from pylablib.devices import Thorlabs

class powermeter(Thorlabs.PM160):
    def __init__(self, port='USB0::0x1313::0x8078::P0048717::0::INSTR'):
        # Call the parent class constructor to initialize the connection
        super().__init__(port)
        self.connected = True  # Assume successful connection if no exception is raised
        print(f"Power meter connected on port: {port}")

    def disconnect(self):
        """Handles the disconnection from the power meter."""
        try:
            self.close()  # Call the close method from the parent class
            self.connected = False
            print(f"Power meter on {self.port} disconnected.")
        except Exception as e:
            print(f"Error while disconnecting power meter on {self.port}: {e}")

    def __del__(self):
        """Ensures the power meter is disconnected when the object is deleted."""
        if self.connected:
            self.disconnect()
