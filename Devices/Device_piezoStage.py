# -*- coding: utf-8 -*-
"""
Created on Thu Sep 6 10:30:02 2024

@author: Johannes Eberle
@functionality: This is the Thorlabs piezo stage (linear stage and rotation stage). In this code, we inherit from the Thorlabs.ElliptecMotor class in pylablib with all the methods associated to it.

"""
from pylablib.devices import Thorlabs

class piezoStage(Thorlabs.ElliptecMotor):
    def __init__(self, com_port="COM8"):
        # Call the parent class constructor to initialize the connection
        super().__init__(com_port)
        self.connected = True  # Assume successful connection if no exception is raised

    def disconnect(self):
        """Handles the disconnection from the stage."""
        try:
            self.close()  # Call the close method from the parent class
            self.connected = False
            print(f"Stage on {self.port} disconnected.")
        except Exception as e:
            print(f"Error disconnecting stage on {self.port}: {e}")

    def __del__(self):
        """Ensures the stage is disconnected when the object is deleted."""
        if self.connected:
            self.disconnect()
