import anvil

class MapExporter:

    def __init__(self, in_data, out_path):
        self.in_data = in_data
        self.out_path = out_path
        self.regions = dict()

    def region_for(self, x, z):
        x_key = x // 512
        z_key = z // 512
        key = (x_key, z_key)
        if key not in self.regions:
            self.regions[key] = anvil.EmptyRegion(x_key, z_key)
        return self.regions[key]

    def save(self):
        pass

    def process(self):

        stone = anvil.Block('minecraft', 'stone')

        for d in self.in_data:
            x, z, elevation = d
            region = self.region_for(x, z)

            region.set_block(stone, x, elevation, z)

        self.save()