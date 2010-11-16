from pytyle.tile_auto import AutoTile

class Maximal(AutoTile):
    def __init__(self, monitor):
        AutoTile.__init__(self, monitor)

    def tile(self):
        AutoTile.tile(self)

        if not self.store.all():
            return

        # Do master last, in case decorations are disabled
        # and we need to draw the "active" border (so it
        # over laps the "inactive" borders).
        for cont in sorted(self.store.all(), reverse=True):
            cont.moveresize(
                self.monitor.wa_x,
                self.monitor.wa_y,
                self.monitor.wa_width,
                self.monitor.wa_height
            )

        # If we've made it this far, then we've supposedly tiled correctly
        self.error_clear()

    def decrement_masters(self):
        pass

    def increment_masters(self):
        pass
