from workspace import Workspace
from monitor import Monitor
from state import STATE
from autostore import AutoStore

class Tile(object):
    TILING = {}

    def __init__(self, wsid, mid):
        self.workspace = Workspace.WORKSPACES[wsid]
        self.monitor = Monitor.MONITORS[wsid][mid]

    def tile(self):
        pass

    @staticmethod
    def dispatch(tiler, command):
        wsid, mid = STATE.get_active_wsid_and_mid()

        # Keep track of current tilers...
        if wsid not in Tile.TILING:
            Tile.TILING[wsid] = {}

        if mid not in Tile.TILING[wsid]:
            Tile.TILING[wsid][mid] = tiler(wsid, mid)

        t = Tile.TILING[wsid][mid]

        if hasattr(t, command):
            getattr(t, command)()
        else:
            raise Exception('Invalid command %s' % command)

class AutoTile(Tile):
    def __init__(self, wsid, mid):
        Tile.__init__(self, wsid, mid)

        self.store = AutoStore()

        for win in STATE.iter_windows(self.workspace.id, self.monitor.id):
            self.store.add(win.id)

# We need two types of storage mechanisms for tiling windows...
# Firstly, for *just* the auto tiling layouts, we need a tile store
# that keeps track of which windows are masters and which are slaves...
# The store also says which windows should get which status when
# appropriate. Secondly, we need a grid structure that is available
# to any tiling layout--but is the horsepower of the manual tiler.
# i.e., The grid would be helpful in auto layouts like Vertical
# or Horizontal, but not cascade.
