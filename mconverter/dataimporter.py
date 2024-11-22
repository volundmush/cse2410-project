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
        self.elevation_values = list()
        self.dem_clean = None
        self.min_elevation = 0.0
        self.max_elevation = 0.0
        self.min_lon = 0.0
        self.min_lat = 0.0
        self.max_lon = 0.0
        self.max_lat = 0.0
        self.mid_lon = 0.0
        self.mid_lat = 0.0
        self.minecraft_min_y = 0
        self.minecraft_max_y = 0
        self.minecraft_height_range = 0
        self.sea_level_elevation = 0.0
        self.sea_level_proportion = 0.0
        self.minecraft_sea_level_y = 0
        self.sea_level_offset = 0

    def calculate_parameters(self):
        dem = rioxarray.open_rasterio(self.in_file)

        nodata_value = dem.rio.nodata
        self.dem_clean = dem.where(dem != nodata_value, np.nan)

        # Approximate center of your DEM data
        self.min_lon, self.min_lat, self.max_lon, self.max_lat = self.dem_clean.rio.bounds()

        # Get our midpoints for the origin (0,0) of our new coordinate system
        self.mid_lon = (self.min_lon + self.max_lon) / 2
        self.mid_lat = (self.min_lat + self.max_lat) / 2

        # Compute min_elevation and max_elevation before the loops
        self.elevation_values = self.dem_clean.values[0].flatten()
        self.elevation_values = self.elevation_values[~np.isnan(self.elevation_values)]
        self.min_elevation = np.min(self.elevation_values)
        self.max_elevation = np.max(self.elevation_values)

        print(f"Minimum elevation: {self.min_elevation} meters")
        print(f"Maximum elevation: {self.max_elevation} meters")

        # Minecraft height parameters
        self.minecraft_min_y = -64
        self.minecraft_max_y = 319
        self.minecraft_height_range = self.minecraft_max_y - self.minecraft_min_y

        # Real-world sea level elevation
        self.sea_level_elevation = 0.0  # Adjust if necessary

        # Find the proportion of sea level in the elevation range
        self.sea_level_proportion = (self.sea_level_elevation - self.min_elevation) / (self.max_elevation - self.min_elevation)

        # Corresponding Minecraft Y-coordinate for sea level
        self.minecraft_sea_level_y = self.sea_level_proportion * self.minecraft_height_range + self.minecraft_min_y

        # Compute the offset to align with Minecraft's sea level at Y=62
        self.sea_level_offset = 62 - self.minecraft_sea_level_y

    def get_regions(self):
        # Calculate the starting and maximum X coordinates in Minecraft units
        start_x = int((self.min_lon - self.mid_lon) * meters_per_degree_lon)
        max_x = int((self.max_lon - self.mid_lon) * meters_per_degree_lon)

        # Calculate the starting and maximum Z coordinates in Minecraft units
        start_z = int(-(self.max_lat - self.mid_lat) * meters_per_degree_lat)
        max_z = int(-(self.min_lat - self.mid_lat) * meters_per_degree_lat)

        # Align start_x and start_z down to the nearest lower multiple of 512
        aligned_start_x = (start_x // 512) * 512
        aligned_start_z = (start_z // 512) * 512

        # Align max_x and max_z up to the nearest higher multiple of 512
        aligned_max_x = ((max_x + 511) // 512) * 512
        aligned_max_z = ((max_z + 511) // 512) * 512

        cur_z = aligned_start_z

        while cur_z < aligned_max_z:
            cur_x = aligned_start_x

            while cur_x < aligned_max_x:
                region_x = cur_x // 512
                region_z = cur_z // 512
                yield region_x, region_z

                cur_x += 512
            cur_z += 512

    def calculate_lat(self, z):
        return self.mid_lat - z / meters_per_degree_lat

    def calculate_lon(self, x):
        return self.mid_lon + x / meters_per_degree_lon

    def get_elevation(self, x, z):
        elevation = self.dem_clean.sel(x=x, y=self.calculate_lat(z), method='nearest').values[0]
        if math.isnan(elevation):
            elevation = self.min_elevation  # Default to min_elevation or set to sea level

        # Normalize the elevation to Minecraft's Y-coordinate
        y_minecraft = ((elevation - self.min_elevation) / (self.max_elevation - self.min_elevation)) * self.minecraft_height_range + self.minecraft_min_y

        # Apply sea level offset
        y_minecraft += self.sea_level_offset

        # Ensure Y-coordinate is within Minecraft's limits and convert to integer
        y_minecraft = int(np.clip(y_minecraft, self.minecraft_min_y, self.minecraft_max_y))
        return y_minecraft