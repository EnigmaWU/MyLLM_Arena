# Example 1

def bubble_sort(arr):
    n = len(arr)
    # Traverse through all array elements
    for i in range(n):
        # Last i elements are already in place
        for j in range(0, n-i-1):
            # Traverse the array from 0 to n-i-1
            # Swap if the element found is greater than the next element
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr


# Example 2

import pandas as pd
import numpy as np

# Load weather data from CSV file into a DataFrame
weather_df = pd.read_csv('april2024_station_data.csv')

# Convert wind speed and direction columns to numpy arrays for faster computation
wind_speed = weather_df['wind_speed'].to_numpy()
wind_direction = weather_df['wind_direction'].to_numpy()

# Convert wind direction from degrees to radians using numpy's built-in function
wind_direction_rad = np.deg2rad(wind_direction)