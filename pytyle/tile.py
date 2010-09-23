from workspace import Workspace
from monitor import Monitor
from window import Window
from state import STATE
from autostore import AutoStore

class Tile(object):
    TILING = {}
    queue = set()

    def __init__(self, wsid, mid):
        self.workspace = Workspace.WORKSPACES[wsid]
        self.monitor = Monitor.MONITORS[wsid][mid]
        self.tiling = False

    def tile(self):
        self.tiling = True

    def untile(self):
        self.tiling = False

    def needs_tiling(self):
        Tile.queue.add(self)

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
            if t.tiling or command == 'tile':
                getattr(t, command)()
        else:
            raise Exception('Invalid command %s' % command)

    # This doesn't just check if the tiler exists, but also
    # if the tiler is active.
    @staticmethod
    def lookup(wsid, mid):
        if wsid in Tile.TILING and mid in Tile.TILING[wsid] and Tile.TILING[wsid][mid].tiling:
            return Tile.TILING[wsid][mid]
        return None

    @staticmethod
    def iter_tilers():
        for wsid in Tile.TILING:
            for mid in Tile.TILING[wsid]:
                yield Tile.TILING[wsid][mid]

    @staticmethod
    def exec_queue():
        for tiler in Tile.queue:
            tiler.tile()
        Tile.queue = set()

    @staticmethod
    def sc_workspace_or_monitor(wid, old_wsid, old_mid, new_wsid, new_mid):
        old_tiler = Tile.lookup(old_wsid, old_mid)
        new_tiler = Tile.lookup(new_wsid, new_mid)

        if old_tiler:
            old_tiler.remove(wid)

        if new_tiler:
            new_tiler.add(wid)

    @staticmethod
    def sc_windows(added, removed):
        for win in added:
            tiler = Tile.lookup(win.monitor.workspace.id, win.monitor.id)
            if tiler:
                tiler.add(win.id)

        for win in removed:
            tiler = Tile.lookup(win.monitor.workspace.id, win.monitor.id)
            if tiler:
                tiler.remove(win.id)

class AutoTile(Tile):
    def __init__(self, wsid, mid):
        Tile.__init__(self, wsid, mid)

        self.store = AutoStore()

        for win in STATE.iter_windows(self.workspace.id, self.monitor.id):
            self.add(win.id)

    def tile(self):
        Tile.tile(self)

        if not self.store:
            self.store = AutoStore()

            for win in STATE.iter_windows(self.workspace.id, self.monitor.id):
                self.add(win.id)

    def untile(self):
        Tile.untile(self)

        if self.store:
            for wid in self.store.all()[:]:
                Window.lookup(wid).original_state()
                self.store.remove(wid)

            self.store = None

    def add(self, wid):
        self.store.add(wid)
        self.needs_tiling()

    def remove(self, wid):
        self.store.remove(wid)
        self.needs_tiling()

    def make_active_master(self):
        print 'Make active master'

# We need two types of storage mechanisms for tiling windows...
# Firstly, for *just* the auto tiling layouts, we need a tile store
# that keeps track of which windows are masters and which are slaves...
# The store also says which windows should get which status when
# appropriate. Secondly, we need a grid structure that is available
# to any tiling layout--but is the horsepower of the manual tiler.
# i.e., The grid would be helpful in auto layouts like Vertical
# or Horizontal, but not cascade.
