# G15.2_C_center

These codes are adapted from G13 to communcate with the devices in G15.2.

A few updates:
1. changed form scatter plot to pixel images
2. added a param "liveplot" in APDscanAttocube (one can choose whether they want to lively plot the data or not)
3. Running the Device scripts individually activates the connection to their intended Device. DeviceManager then checks whether those connections are good or bad and they are directly imported to mains.py (i.e. no need to connect to the devices everytime when starting a measurement).
