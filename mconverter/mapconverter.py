class MapConverter:

    def __init__(self, in_data):
        self.in_data = in_data

    def process(self):
        """
        The input data is a stream of (x, z, elevation)

        We must return one where we expand the elevation data to lay a foundation.
        """
        for d in self.in_data:
            start_elevation = -64
            x, z, elevation = d
            while start_elevation < elevation:
                yield (x, z, start_elevation)
                start_elevation += 1