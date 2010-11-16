from tile import Tile
from container import Container

class ManualTile(Tile):
    def __init__(self, monitor):
        Tile.__init__(self, monitor)
