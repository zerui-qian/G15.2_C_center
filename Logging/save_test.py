import sys
import os
sys.path.append(os.path.abspath(r'C:\Users\QPG\Documents\Python Scripts\johannes\Control code\Logging'))
import save
import numpy as np

a = {
    "measurement": "Test",
    "name": "Alice",
    "age": 25,
    "city": "Zurich"
}

b_arr1 = [0,1,2,3,4,5,6,7,8,9]
b_arr2 = [234, 234, 234, 1234, 456, 234, 1234, 657, 323, 879]

b = {
    "arr1": b_arr1,
    "arr2": b_arr2,
    "city": "Zurich"
} 

times = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) *60*60
counts = [2345, 345, 456, 678, 678, 343, 3467, 345, 4657, 678]

c = {
    "Time": times.tolist(),
    "APD counts": counts,
    "city": "Zurich"
} 

save.save_measurement(b, a) 