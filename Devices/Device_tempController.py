# -*- coding: utf-8 -*-
"""
Created on Thu Sep 6 11:28:12 2024

@author: Johannes Eberle
@functionality: This is the Covesion temperature controller. In this code, we inherit from the OC class provided by covesion with all the methods associated to it. I have added a few additional methods.

"""
import sys
import os
import Device_OC as OC

class tempController(OC.OC):
    def __init__(self, port="COM9"):
        # Call the parent class constructor to initialize the connection
        super().__init__(port)
        self.enable()  # Automatically enable the controller upon initialization

    def disconnect(self):
        """Disconnect the temperature controller."""
        self.OC_close()  # Call the parent class method to close the connection
