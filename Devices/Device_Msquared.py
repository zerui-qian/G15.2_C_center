# -*- coding: utf-8 -*-
"""
Created on Thu Sep 6 10:30:02 2024

@author: Johannes Eberle
@functionality: This is the M2 SolsTiS laser. In this code, we inherit from the M2.Solstis class in pylablib with all the methods associated to it.

"""

from pylablib.devices import M2

class Msquared(M2.Solstis):
    def __init__(self):
        # Set default connection parameters
        ip_address = "172.31.88.153"
        port = 39933
        timeout = 180.0

        # Call the parent class (M2.Solstis) constructor with the parameters
        super().__init__(ip_address, port, timeout=timeout)

    def disconnect(self):
        super().close()