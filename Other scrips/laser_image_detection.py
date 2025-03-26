# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 10:02:36 2024

@author: QPG
"""

import os
import numpy as np
import cv2
from datetime import datetime


def detect_laser_points(file_path, file_name):
    """
    Detect the brightest laser point in an image based on brightness.

    Args:
        file_path (str): Path to the folder containing the images.
        file_name (str): Name of the image file.

    Returns:
        tuple: Coordinates (x, y) of the detected laser point.
    """
    # Load the image
    full_image_path = os.path.join(file_path, file_name)
    image = cv2.imread(full_image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Image at path {full_image_path} not found.")

    # Find the brightest point in the image
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(image)
    return max_loc

def overlay_laser_points(camera_image_path, file_path, corner_file_names):
    """
    Detect the laser points from four images, overlay them on the camera image, and draw the scanning area.

    Args:
        camera_image_path (str): Path to the camera image file.
        file_path (str): Path to the folder containing the corner images.
        corner_file_names (list): List of file names for the four images with the laser positioned at each corner.

    Returns:
        None
    """
    if len(corner_file_names) != 4:
        raise ValueError("Exactly four images with the laser at each corner are required to define the scanning area.")

    # Load the camera image
    camera_image = cv2.imread(camera_image_path)
    if camera_image is None:
        raise FileNotFoundError(f"Camera image at path {camera_image_path} not found.")

    # Detect laser points in each of the corner images
    laser_points = []
    for file_name in corner_file_names:
        point = detect_laser_points(file_path, file_name)
        laser_points.append(point)

    # Sort the laser points in a consistent order (e.g., top-left, top-right, bottom-right, bottom-left)
    laser_points = sorted(laser_points, key=lambda p: (p[1], p[0]))

    # Draw the detected laser points and the polygon representing the scanning area
    for point in laser_points:
        cv2.circle(camera_image, point, radius=5, color=(0, 0, 255), thickness=-1)  # Draw laser points in red

    # Draw the polygon connecting the four laser points
    laser_points_np = np.array(laser_points, dtype=np.int32)
    cv2.polylines(camera_image, [laser_points_np], isClosed=True, color=(0, 255, 0), thickness=2)  # Draw polygon in green

    # Display the result in a new window
    cv2.imshow("Overlayed Laser Points and Scanning Area", camera_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage:
# overlay_laser_points("camera_image.png", ["laser_image1.png", "laser_image2.png", "laser_image3.png", "laser_image4.png"])