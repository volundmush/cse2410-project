import rioxarray
import numpy as np
import xarray as xr
import rasterio
import pyproj
import math

from affine import Affine

from pathlib import Path

meters_per_degree_lat = 111_000  # Approximate value
meters_per_degree_lon = 85_000   # Approximate value at 45 degrees latitude

class DataImporter:

    def __init__(self, in_file: Path):
        if not in_file:
            raise ValueError("Input file is required")
        if not in_file.exists():
            raise FileNotFoundError(f"File {in_file} not found")
        if not in_file.is_file():
            raise ValueError(f"{in_file} is not a file")
        self.in_file = in_file

    def process(self):
        dem = rioxarray.open_rasterio(self.in_file)

        nodata_value = dem.rio.nodata
        dem_clean = dem.where(dem != nodata_value, np.nan)

        # Approximate center of your DEM data
        min_lon, min_lat, max_lon, max_lat = dem_clean.rio.bounds()

        print(f"Longitude range: {min_lon} to {max_lon}")
        print(f"Latitude range: {min_lat} to {max_lat}")

        # get our midpoints for the origin (0,0) of our new coordinate system.
        mid_lon = (min_lon + max_lon) / 2
        mid_lat = (min_lat + max_lat) / 2

        # Assuming 'elevation_values' is a NumPy array of your elevation data
        elevation_values = dem_clean.values[0].flatten()

        # Remove NaN values
        elevation_values = elevation_values[~np.isnan(elevation_values)]

        # Find minimum and maximum elevations
        min_elevation = np.min(elevation_values)
        max_elevation = np.max(elevation_values)

        print(f"Minimum elevation: {min_elevation} meters")
        print(f"Maximum elevation: {max_elevation} meters")

        minecraft_min_y = -64
        minecraft_max_y = 319
        minecraft_height_range = minecraft_max_y - minecraft_min_y  # Total of 384 blocks

        # Normalize the elevations
        y_minecraft = ((elevation_values - min_elevation) / (max_elevation - min_elevation)) * (minecraft_height_range) + minecraft_min_y

        # Convert to integers (since block positions are integers)
        y_minecraft = y_minecraft.astype(int)

        # Real-world sea level elevation
        sea_level_elevation = 0.0  # Adjust if your dataset's sea level is at a different elevation

        # Find the proportion of sea level in the elevation range
        sea_level_proportion = (sea_level_elevation - min_elevation) / (max_elevation - min_elevation)

        # Corresponding Minecraft Y-coordinate for sea level
        minecraft_sea_level_y = sea_level_proportion * minecraft_height_range + minecraft_min_y

        # Compute the offset to align with Minecraft's sea level at Y=62
        sea_level_offset = 62 - minecraft_sea_level_y

        # Apply the offset to all Y-coordinates
        y_minecraft += sea_level_offset

        # Ensure Y-coordinates are within Minecraft's limits
        y_minecraft = np.clip(y_minecraft, minecraft_min_y, minecraft_max_y)

        # ChatGPT, part I need help with begins below.

        # Calculate the starting and maximum X coordinates in Minecraft units
        start_x = int((min_lon - mid_lon) * meters_per_degree_lon)
        max_x = int((max_lon - mid_lon) * meters_per_degree_lon)

        # Calculate the starting and maximum Z coordinates in Minecraft units
        start_z = int(-(max_lat - mid_lat) * meters_per_degree_lat)
        max_z = int(-(min_lat - mid_lat) * meters_per_degree_lat)

        def normalized_elevation(e):
            return ((e - min_elevation) / (max_elevation - min_elevation)) * (minecraft_height_range) + minecraft_min_y

        cur_y = start_z

        while cur_y < max_y:
            cur_x = start_x
            # update our cur_lon...
            cur_lon = <placeholder>
            while cur_x < max_x:
                # calculate and yield something
                cur_lat = <placeholder>
                e = dem_clean.sel(x=cur_lat, y=cur_lon, method='nearest')
                e2 = normalized_elevation(e)
                yield cur_x, cur_y, e2
                cur_x += 1
            cur_y += 1
