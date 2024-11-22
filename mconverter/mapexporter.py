import amulet
from pathlib import Path

from amulet.api.errors import ChunkLoadError, ChunkDoesNotExist
from amulet.api.chunk import Chunk
from amulet.api.block import Block

class MapExporter:

    def __init__(self, importer, out_path: Path):
        self.importer = importer
        self.out_path = out_path

    def process(self):
        # Load the Minecraft world
        world = amulet.load_level(str(self.out_path))
        dimension = "minecraft:overworld"

        # Block to place (stone in this case)
        stone = Block("minecraft", "stone")

        # Clear all existing chunks in the dimension
        for cx, cz in world.all_chunk_coords(dimension):
            world.delete_chunk(cx, cz, dimension)
        world.save()

        # Get the region bounds from the importer
        for region_x, region_z in self.importer.get_regions():
            full_x = region_x * 512
            full_z = region_z * 512

            # Process all chunks in the region (32x32 chunks per region)
            for chunk_x in range(region_x * 32, (region_x + 1) * 32):
                for chunk_z in range(region_z * 32, (region_z + 1) * 32):
                    print(f"Processing chunk ({chunk_x}, {chunk_z})")

                    # Create or load the chunk
                    chunk = Chunk(chunk_x, chunk_z)
                    stone_id = chunk.block_palette.get_add_block(stone)

                    # Process all blocks in the chunk
                    for x in range(16):
                        for z in range(16):
                            global_x = full_x + (chunk_x % 32) * 16 + x
                            global_z = full_z + (chunk_z % 32) * 16 + z

                            # Get longitude, latitude, and elevation
                            longitude = self.importer.calculate_lon(global_x)
                            latitude = self.importer.calculate_lat(global_z)
                            elevation = self.importer.get_elevation(longitude, latitude)

                            # Normalize elevation to Minecraft height range
                            max_y = min(elevation, self.importer.minecraft_max_y)

                            # Set blocks up to the max_y
                            for y in range(self.importer.minecraft_min_y, max_y):
                                chunk.blocks[x, y, z] = stone_id

                    # Save the chunk
                    world.put_chunk(chunk, dimension)
                    chunk.changed = True

        # Save all changes to the world
        world.save()
        world.close()
        print("World export completed.")
