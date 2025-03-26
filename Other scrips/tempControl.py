# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 11:44:50 2024

@author: QPG
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 10:02:11 2024

@author: QPG
"""
import time
from datetime import date, timedelta, datetime
import numpy as np
import sys
import os
import csv
import pandas as pd
import copy
import scipy.interpolate

sys.path.append(os.path.abspath(r'C:\Users\QPG\Documents\Python Scripts\johannes\OC_Python - Release'))
import OC


def temp_opt(oc, pm, laser, set_wv, max_power, opt_power, csv_filename, lim=2, stabilize_time=5, fast_opt=False, sign=1):
    print("Adjusting temperature...")
    time.sleep(2)
    initial_temp = oc.get_temperature()
    initial_power = pm.get_power()*1e3
    print('Initial power: ', initial_power)
    power = initial_power


    if initial_power > max_power:
        print('initial_power >= max_power')
        return initial_temp, True, 0, 0
        
    temps = []
    powers = []
    wvs = []
    times = []

    max_power_iteration = initial_power
    max_temp_iteration = initial_temp

    temp = initial_temp
    success = True
    laser_tunings = 0
    tuning_problems = 0

    while max_power_iteration < max_power:
        
        
        wv = laser.get_fine_wavelength() * 1e9
        
        
        if np.abs(wv - set_wv) > 1e-2:
            laser_tunings += 1
            print("Tuning wavelength in temp control code")
            try:
                laser.lock_wavemeter(lock=True, sync=False, error_on_fail=True)
                laser.fine_tune_wavelength(set_wv*1e-9)
            except:
                print("Tuning didn't work")
                tuning_problems += 1
                pass

        if power < 0.1 * max_power:
            stepSize = 0.1
        elif power < 0.5 * max_power:
            stepSize = 0.02
        elif power < 0.8 * max_power:
            stepSize = 0.02
        else:
            # stepSize = 0.01  # divide by two for 0.01nm step size of wavelength - actually don't
            stepSize = 0.01 # before: 0.02
        temp += sign * stepSize
        print('Increasing temperature by ', sign*stepSize)
        #sys.stdout = open(os.devnull,'w')  # Disabling output stream for the settle function since it prints too much
        settle_oc(oc, temp, stability_range=stepSize, stabilize_time=stabilize_time, store_wv=False)

        if opt_power:
            temps.append(oc.get_temperature())
            powers.append(pm.get_power()*1e3)
            wvs.append(laser.get_fine_wavelength())
            times.append(time.time())

        #sys.stdout = sys.__stdout__  # Enabling output stream
        power = pm.get_power()*1e3
        print('Power: ', power)
        if power > max_power_iteration:
            max_power_iteration = power
            max_temp_iteration = temp

        if np.abs(temp - initial_temp) >= lim:
            #temp = max_temp_iteration
            temp = initial_temp
            settle_oc(oc, temp, store_wv=False)
            if opt_power:
                break
            else:
                return max_temp_iteration, False, laser_tunings, tuning_problems

        # if not fast_opt and power > self.max_power*0.7:
        if (not fast_opt) and (power > max_power*0.8): #before: 0.9
            print("Power: ", power)
            print("Power high. Sleeping for 15 seconds.")
            time.sleep(15)
            power = pm.get_power()*1e3
            print("New power: ", power)

    if not opt_power:
        optimal_temp = oc.get_temperature()
        settle_oc(oc, optimal_temp, stability_range=0.1, stabilize_time=stabilize_time, store_wv=False)
        return optimal_temp, success, laser_tunings, tuning_problems

    else:
        print("Recording temperature curve")
        end_temp = copy.copy(temp)
        while temp < end_temp + sign*1:
            if power < 0.5 * max_power:
                temp += sign*0.1
            else:
                temp += sign*0.08
    
            print('Increasing temperature to', temp)
            #sys.stdout = open(os.devnull, 'w')
            settle_oc(oc, temp, stability_range=0.1, stabilize_time=stabilize_time)
            #sys.stdout = sys.__stdout__

            temps.append(oc.get_temperature())
            powers.append(pm.get_power()*1e3)
            wvs.append(laser.get_fine_wavelength())
            times.append(time.time())

        optimal_power = np.max(powers)
        optimal_temp = temps[np.argmax(powers)]
        print("Max. power: ", optimal_power)
        print("Optimal temperature: ", optimal_temp)

        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([0, 0, laser.get_fine_wavelength(), 0])
            writer.writerow([temps, powers, wvs, times])

        settle_oc(oc, optimal_temp - 0.2)
        return optimal_temp, success, laser_tunings, tuning_problems



def vary_power(self, temp_step=0.02):
    if self.first_step:
        self.first_step = False
        wv = self.measure_wv(color='green')
        wv_nir = 1 / (1 / wv - 1 / 1550)
        opt_start_t = 7.12902056 * wv_nir - 5780.69462183
        self.settle_oc(oc, opt_start_t - 2)
        p = self.max_power
        self.max_power = 0.5
        self.temp, success = self.temp_opt(fast_opt=True)
        self.max_power = p
        for i in range(0,12):
            self.measure_wv(color='green')
            time.sleep(5)
    self.temp = self.temp + temp_step
    self.settle_oc(oc, temp, stabilize_time = 45)

    power = self.pm.get_power()*1e3
    for i in range(0,6):
        self.measure_wv(color='green')
        time.sleep(5)

    if not self.max_power_reached and power > self.max_power:
        self.max_power_reached = True
    elif self.max_power_reached and power < self.max_power:
        self.finished = True

    return power, self.finished

def connect_oc(addr_oc):
    oc = OC.OC(addr_oc)
    oc.enable()
    #print(oc.get_status())
    return oc

def settle_oc(oc, target_temperature, stability_range=0.1, stabilize_time=5, ramp_rate=0.1, lower=False,
              store_wv=False):
    if target_temperature > 200 or target_temperature < 30:
        print('Error: Temperature setting out of bounds!')
        return -1
    # set temperature and enable temperature control
    success = oc.set_temperature(target_temperature)
    oc.enable()
    oc.set_ramp_rate(ramp_rate)
    # Monitor temperature and test for stability
    in_range = False
    time_in_range = timedelta()
    stable = False

    print("Waiting for target temperature to stabilize...")

    while not stable:

        # Get the status of the controller. This will return both the
        # setpoint that the controller is aiming for, and the current
        # temperature of the oven.
        try:
            oc.get_status()
        except:
            print('Cannot read temperature')
            continue

        # Fault check
        if not (oc.fault_code[0] == 0):
            # If a fault is seen, it is logged in the fault_queue with the fault type
            # and the time is occured
            print(*oc.fault_queue, sep='\n')

        if lower:
            temp_diff = oc.temperature[0] - oc.setpoint[0]
        else:
            temp_diff = abs(oc.temperature[0] - oc.setpoint[0])

        if temp_diff <= stability_range:
            if not in_range:
                in_range = True
                restart = True

            if in_range and restart:
                t0 = datetime.now()
                restart = False
            else:
                time_in_range = datetime.now() - t0

                if time_in_range.seconds >= stabilize_time:
                    stable = True
        else:
            in_range = False
            time_in_range = timedelta()
        time.sleep(1)

    print("Target temperature stable")



