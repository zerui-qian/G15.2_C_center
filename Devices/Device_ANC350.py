# -*- coding: utf-8 -*-
"""
Created on Thu Sep 4 17:18:07 2024

@author: Johannes Eberle
@functionality: This is the attocube device which can scan in x, y and z direction

The code is originally from Thomas Fink, Quantum Photonics Group, ETH Zurich

"""
import time
import ctypes
import scipy as sp
import numpy as np
import logging
import functools

class ANC350(object):
    
    
    
    def __init__(self, DevNo=0):
        
        self._logger = logging.getLogger(self.__class__.__name__)        
        dll_path='anc350v4.dll'
        try:
            self._dll = ctypes.windll.LoadLibrary(dll_path)
        except RuntimeError:
            print("Could not find dll.")
        self._discover()
        self._connect(DevNo)
        
        
    def _errorhandler(func):
        @functools.wraps(func)  
        def func_wrapper(*args,**kwargs):
            ret = func(*args, **kwargs)
            if args[0]._res != 0:                
                raise RuntimeError(args[0]._parse_errorcode(args[0]._res))
#                args[0]._logger.error(args[0]._parse_errorcode(args[0]._res))
            return ret
        return func_wrapper
            
            
    def _parse_errorcode(self,errcode):
        switcher = {
            -1: "Unspecified error.",
            1: "Receive timed out.",
            2: "No connection was established.",
            3: "Error accessing the USB driver.",
            7: "Can't connect, device already in use.",
            8: "Unknown error.",
            9: "Invalid device number used in call.",
            10: "Invalid axis number in function call.",
            11: "Parameter in call is out of range.",   
            12: "Function not available for device type.",                 
        }
        return switcher.get(errcode,"No errorcode found.")


    @_errorhandler
    def _discover(self,InterfaceTypes='All'):
        '''
        Discover Devices
        
        The function searches for connected ANC350RES devices on USB and 
        LAN and initializes internal data structures per device. Devices
        that are in use by another application or PC are not found. 
        The function must be called before connecting to a device and
        must not be called as long as any devices are connected.
        
        The number of devices found is returned. In subsequent functions, 
        devices are identified by a sequence number that must be less than
        the number returned.
        
        Parameters
            ifaces	Interfaces where devices are to be searched
            
            devCount	Output: number of devices found        
        '''
        IntType = {
            'None': 0,
            'USB':  1,
            'TCP':  2,
            'All':  3
            }.get(InterfaceTypes)
        found = ctypes.c_uint32()
        self._dll.ANC_discover.argtypes = [ctypes.c_uint32,
                                           ctypes.POINTER(ctypes.c_uint32)
                                           ]
        self._res = self._dll.ANC_discover(IntType,ctypes.byref(found))
        self._logger.info("ANC350v4 found: %i." % found.value)            
        return found.value        
                        

    @_errorhandler                        
    def _connect(self, DevNo):
        '''
        Connect Device

        Initializes and connects the selected device. This has to be done before any access to control variables or measured data.

        Parameters
            devNo	Sequence number of the device. Must be smaller than the devCount from the last ANC_discover call.
            
            device	Output: Handle to the opened device, NULL on error
        '''
        
        self._handle = ctypes.c_void_p()# ctypes.c_ulong()
        self._dll.ANC_connect.argtypes = [ctypes.c_uint32,
                                          ctypes.c_void_p#ctypes.POINTER(ctypes.c_int32)
                                          ]
        
        #self._handle = ctypes.c_int32()
        #self._dll.ANC_connect.argtypes = [ctypes.c_uint32,
        #                                  ctypes.POINTER(ctypes.c_int32)
        #                                  ]
        #self._res = self._dll.ANC_connect(DevNo,ctypes.byref(self._handle))
        DevNo = ctypes.c_uint32(DevNo)
        self._res = self._dll.ANC_connect(DevNo, ctypes.byref(self._handle))
        #self._logger.info("ANC350 connected. Device handle %i." % self._handle.value)
        return self._handle.value

         
    @_errorhandler
    def _disconnect(self):
        '''
        Disconnect Device

        Closes the connection to the device. The device handle becomes invalid.

        Parameters
            device	Handle of the device to close
        '''
        self._dll.ANC_disconnect.argtypes = [ctypes.c_void_p]
        self._res = self._dll.ANC_disconnect(self._handle)
        
        
    @_errorhandler
    def close(self):
        self._disconnect()
        self._logger.info("ANC350 disconnected.")

        
    @_errorhandler
    def _getPosition(self,axis):
        '''
        Read Current Position

        Retrieves the current actuator position. For linear type actuators the position unit is m; for goniometers and rotators it is degree.

        Parameters
            device	Handle of the device to access
            axisNo	Axis number (0 ... 2)
            position	Output: Current position [m] or [°]
        '''
        position = ctypes.c_double()
        self._dll.ANC_getPosition.argytpes = [ctypes.c_void_p,
                                              ctypes.c_uint32
                                              #ctypes.POINTER(ctypes.c_double)
                                              ]
        self._res = self._dll.ANC_getPosition(self._handle,axis,ctypes.byref(position))
        return position.value /1e-6
        
        
    @property
    @_errorhandler
    def Position(self):
            pos = []
            for axis in range(3):
                pos.append(self._getPosition(axis))
            return np.array(pos)
    
    
    @_errorhandler
    def _measureCapacitance(self,axis):
        '''
        Measure Motor Capacitance

        Performs a measurement of the capacitance of the piezo motor and returns the result. If no motor is connected, the result will be 0. The function doesn't return before the measurement is complete; this will take a few seconds of time.

        Parameters
            device	Handle of the device to access
            axisNo	Axis number (0 ... 2)
            cap	Output: Capacitance [F]
        '''
        cap = ctypes.c_double()
        self._dll.ANC_measureCapacitance.argytpes = [ctypes.c_void_p,
                                                     ctypes.c_uint32,
                                                     ctypes.POINTER(ctypes.c_double)
                                                     ]
        self._res = self._dll.ANC_measureCapacitance(self._handle,axis,ctypes.byref(cap))
        return cap.value
        
        
    @property
    @_errorhandler
    def Capacitance(self):
        '''
        Measure Motor Capacitance

        Performs a measurement of the capacitance of the piezo motor and returns the result. If no motor is connected, the result will be 0. The function doesn't return before the measurement is complete; this will take a few seconds of time.

        Parameters
            device	Handle of the device to access
            axisNo	Axis number (0 ... 2)
            cap	Output: Capacitance [F]
        '''        
        cap = []
        for axis in range(3):
            cap.append(self._measureCapacitance(axis))
        return np.array(cap)
    

    @property
    @_errorhandler    
    def Frequency(self):
        '''
        Get / Set Frequency.

        Gets / Sets the frequency parameter for an axis

        Parameters
            device	Handle of the device to access
            axisNo	Axis number (0 ... 2)
            frequency	Frequency in Hz, internal resolution is 1 Hz
        '''
        freq = []
        for axis in range(3):
            tmp = ctypes.c_double()
            self._dll.ANC_getFrequency.argytpes = [ctypes.c_void_p,
                                                   ctypes.c_uint32,
                                                   ctypes.POINTER(ctypes.c_double)
                                                   ]
            self._res = self._dll.ANC_getFrequency(self._handle,axis,ctypes.byref(tmp))
            freq.append(tmp.value)
        return np.array(freq)
    @Frequency.setter
    @_errorhandler    
    def Frequency(self,axisfreq):
        axis, freq = axisfreq
        self._dll.ANC_setFrequency.argytpes = [ctypes.c_void_p,
                                               ctypes.c_uint32,
                                               ctypes.c_double
                                               ]
        self._res = self._dll.ANC_setFrequency(self._handle,axis,ctypes.c_double(freq))


    def setDefFreqs(self):
        self.Frequency = [0,20]
        self.Frequency = [1,200]
        self.Frequency = [2,200]


    @property
    @_errorhandler    
    def Amplitude(self):
        '''
        Get / Set Amplitude

        Gets / Sets the amplitude parameter for an axis

        Parameters
            device	Handle of the device to access
            axisNo	Axis number (0 ... 2)
            amplitude	Amplitude in V, internal resolution is 1 mV
        '''
        amp = []
        for axis in range(3):
            tmp = ctypes.c_double()
            self._dll.ANC_getAmplitude.argytpes = [ctypes.c_void_p,
                                                   ctypes.c_uint32,
                                                   ctypes.POINTER(ctypes.c_double)
                                                   ]
            self._res = self._dll.ANC_getAmplitude(self._handle,axis,ctypes.byref(tmp))
            amp.append(tmp.value)
        return np.array(amp)
    @Amplitude.setter
    @_errorhandler    
    def Amplitude(self,axisamp):
        axis, amp = axisamp
        self._dll.ANC_setAmplitude.argytpes = [ctypes.c_void_p,
                                               ctypes.c_uint32,
                                               ctypes.c_double
                                               ]
        self._res = self._dll.ANC_setAmplitude(self._handle,axis,ctypes.c_double(amp))
        
        
    @_errorhandler    
    def setTgtPos(self,axis,pos):
        self._dll.ANC_setTargetPosition.argytpes = [ctypes.c_void_p,
                                                    ctypes.c_uint32,
                                                    ctypes.c_double
                                                    ]
        self._res = self._dll.ANC_setTargetPosition(self._handle,axis,ctypes.c_double(pos))


    @_errorhandler     
    def setPosTracking(self,axis,enable,relative=0):
        self._dll.ANC_startAutoMove.argytpes = [ctypes.c_void_p,
                                                ctypes.c_uint32,
                                                ctypes.c_uint32,
                                                ctypes.c_uint32,
                                                ]
        self._res = self._dll.ANC_startAutoMove(self._handle,axis,enable,relative)


    @_errorhandler     
    def setPosPrecision(self,axis,targetRng):
        self._dll.ANC_setTargetRange.argytpes = [ctypes.c_void_p,
                                                 ctypes.c_uint32,
                                                 ctypes.c_double
                                                 ]
        self._res = self._dll.ANC_setTargetRange(self._handle,axis,ctypes.c_double(targetRng))


    @property                
    @_errorhandler     
    def isMoving(self):
        move = []
        for axis in range(3):
            tmp = ctypes.c_uint32()
            self._dll.ANC_getAxisStatus.argytpes = [ctypes.c_void_p,
                                                    ctypes.c_uint32,
                                                    ctypes.POINTER(ctypes.c_uint32),
                                                    ctypes.POINTER(ctypes.c_uint32),
                                                    ctypes.POINTER(ctypes.c_uint32),
                                                    ctypes.POINTER(ctypes.c_uint32),
                                                    ctypes.POINTER(ctypes.c_uint32),
                                                    ctypes.POINTER(ctypes.c_uint32),
                                                    ctypes.POINTER(ctypes.c_uint32)
                                                    ]
            self._res = self._dll.ANC_getAxisStatus(self._handle,axis,None,None, ctypes.byref(tmp),None,None,None,None)
            move.append(tmp.value)
        return np.array(move)
            
            
    @_errorhandler    
    def SingleStep(self,axis,backward=0):
        self._dll.ANC_startSingleStep.argytpes = [ctypes.c_void_p,
                                                  ctypes.c_uint32,
                                                  ctypes.c_int32,
                                                  ]
        self._res = self._dll.ANC_startSingleStep(self._handle,axis,int(backward))
        
        
    @_errorhandler
    def setTgtPosUm(self,x,y,z):
        tgtPos = [x*10**(-6),y*10**(-6),z*10**(-6)]        
        self._dll.ANC_setTargetPosition.argytpes = [ctypes.c_void_p,
                                                    ctypes.c_uint32,
                                                    ctypes.c_double
                                                    ]
        for axis in range(3):
            self._res = self._dll.ANC_setTargetPosition(self._handle,axis,ctypes.c_double(tgtPos[axis]))
                  

    def steps(self,axis,num):
        for idx in range(abs(num)):
            if num < 0:
                self.SingleStep(axis,1)
            elif num > 0:
                self.SingleStep(axis,0)
            else:
                self._logger.error("Direction not understood. No step made.")
            time.sleep(.01)


    def moveToPos(self,x,y,z):
        tgtPos = np.array([x,y,z])
        self.setTgtPosUm(x,y,z)

        for axis in range(3):
            self.Frequency = [axis,800]        

        for axis in range(3):
            self.setPosPrecision(axis, 0.1 * 10**(-6))
            self.setPosTracking(axis,1)

        #Procede by steps concerning Frequency
            

        
        for i in range(40):
            actPos = self.Position
            if np.linalg.norm(actPos[:] - tgtPos[:]) < 5:
                break
            time.sleep(0.5)
            
        for axis in range(3):
            self.Frequency = [axis,20]

        for i in range(40):
            actPos = self.Position
            if np.linalg.norm(actPos[:] - tgtPos[:]) < 0.5:
                time.sleep(1.0)
                self.setDefFreqs()                
                for axis in range(3):
                    self.setPosTracking(axis,0)
                return 0
            time.sleep(0.5)                
        
        self.setDefFreqs()
        for axis in range(3):
            self.setPosTracking(axis,0)
        return 1
        
    
         
if __name__ == "__main__":
#     #import logging
#     import sys
#     import time
    
#     #logging.basicConfig(stream=sys.stdout,level=logging.INFO)
#     #root_logger = logging.getLogger()
#     #root_logger.setLevel(logging.INFO)   
    
    anc = ANC350()
#     time.sleep(.5)
# #    print(anc._discover())
#     #print(anc.Position)
#     #print(anc.Capacitance)
#     #print(anc.Frequency)
#     #4?print(anc.Amplitude)
# #    anc.Frequency = [0,45]
# #    anc.Amplitude = [0,40.]
#     # anc.close()