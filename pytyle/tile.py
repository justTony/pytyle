from workspace import Workspace
from monitor import Monitor
from container import Container
from window import Window
from state import STATE
from autostore import AutoStore

class Tile(object):
    TILING = {}
    queue = set()

    def __init__(self, wsid, mid):
        self.workspace = Workspace.WORKSPACES[wsid]
        self.monitor = Monitor.MONITORS[wsid][mid]
        self.monitor.tiler = self
        self.tiling = False

    def tile(self):
        self.tiling = True

    def untile(self):
        self.tiling = False

    def needs_tiling(self, override=False):
        if self.tiling or override:
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
            if command == 'tile':
                t.needs_tiling(override=True)
            elif t.tiling:
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
    def iter_tilers(workspaces=None, monitors=None):
        if isinstance(workspaces, int):
            workspaces = [workspaces]

        if isinstance(monitors, int):
            monitors = [monitors]

        for wsid in Tile.TILING:
            if workspaces is None or wsid in workspaces:
                for mid in Tile.TILING[wsid]:
                    if monitors is None or mid in monitors:
                        yield Tile.TILING[wsid][mid]

    @staticmethod
    def exec_queue():
        for tiler in Tile.queue:
            tiler.tile()
        Tile.queue = set()

    @staticmethod
    def sc_windows(added, removed):
        for win in added:
            tiler = Tile.lookup(win.monitor.workspace.id, win.monitor.id)
            if tiler:
                tiler.add(win)

        for win in removed:
            tiler = Tile.lookup(win.monitor.workspace.id, win.monitor.id)
            if tiler:
                tiler.remove(win)

class AutoTile(Tile):
    def __init__(self, wsid, mid):
        Tile.__init__(self, wsid, mid)
        self.store = None
        self.cycle_index = 0

    def tile(self):
        Tile.tile(self)

        if not self.store:
            self.store = AutoStore()

            active = STATE.get_active()

            if active:
                self.add(active)

            for win in STATE.iter_windows(self.workspace.id, self.monitor.id):
                if win != active:
                    self.add(win)

    def untile(self):
        Tile.untile(self)

        if self.store:
            for cont in self.store.all()[:]:
                cont.remove(reset_window=True)

            self.store = None

    def add(self, win):
        if win.tilable() and self.tiling:
            cont = Container(self, win)
            self.store.add(cont)
            self.needs_tiling()

    def remove(self, win, reset_window=False):
        if win.container and self.tiling:
            self.store.remove(win.container)
            win.container.remove(reset_window=reset_window)
            self.needs_tiling()

    def get_active(self):
        active = self.monitor.get_active()

        if active:
            if active.container and active.container in self.store.all():
                return active.container
            else:
                return self.store.all()[0]

        return None

    def get_next(self):
        active = self.get_active()

        if active:
            a = self.store.all()
            return a[(a.index(active) + 1) % len(a)]

        return None

    def get_previous(self):
        active = self.get_active()

        if active:
            a = self.store.all()
            return a[a.index(active) - 1]

        return None

    def float(self):
        active = STATE.get_active()

        if active and active.monitor.workspace.id == self.workspace.id and active.monitor.id == self.monitor.id:
            if not active.floating:
                active.floating = True
                self.remove(active, reset_window=True)
            else:
                active.floating = False
                self.add(active)

    def make_active_master(self):
        if self.store.masters:
            active = self.get_active()
            master = self.store.masters[0]

            if active != master:
                master.switch(active)

    def focus_master(self):
        master = self.store.masters[0]
        if master:
            master.activate()

    def next(self):
        next = self.get_next()

        if next:
            next.activate()

    def previous(self):
        previous = self.get_previous()

        if previous:
            previous.activate()

    def switch_next(self):
        active = self.get_active()
        next = self.get_next()

        if active and next:
            active.switch(next)

    def switch_previous(self):
        active = self.get_active()
        previous = self.get_previous()

        if active and previous:
            active.switch(previous)

    def cycle(self):
        if self.store.masters and self.store.slaves:
            if self.cycle_index >= len(self.store.slaves):
                self.cycle_index = 0

            master = self.store.masters[0]
            slave = self.store.slaves[self.cycle_index]

            master.switch(slave)

            self.cycle_index += 1

    def increment_masters(self):
        self.store.inc_masters()
        self.needs_tiling()

    def decrement_masters(self):
        self.store.dec_masters()
        self.needs_tiling()

    def screen_focus(self, mid):
        new_tiler = Tile.lookup(self.workspace.id, mid)

        if self != new_tiler and new_tiler:
            active = new_tiler.get_active()

            if active:
                active.activate()
            elif new_tiler.store.masters:
                new_tiler.store.masters[0].activate()
            elif new_tiler.store.slaves:
                new_tiler.store.slaves[0].activate()

    def screen_put(self, mid):
        active = self.get_active()
        new_tiler = Tile.lookup(self.workspace.id, mid)

        if new_tiler != self and active and new_tiler:
            active.win.set_monitor(self.workspace.id, mid)
        elif active and self.monitor.id != mid and mid in Monitor.MONITORS[self.workspace.id]:
            mon = Monitor.MONITORS[self.workspace.id][mid]
            active.win.moveresize(mon.wa_x, mon.wa_y, active.w, active.h)

    def screen0_focus(self):
        self.screen_focus(0)

    def screen1_focus(self):
        self.screen_focus(1)

    def screen2_focus(self):
        self.screen_focus(2)

    def screen0_put(self):
        self.screen_put(0)

    def screen1_put(self):
        self.screen_put(1)

    def screen2_put(self):
        self.screen_put(2)


# We need two types of storage mechanisms for tiling windows...
# Firstly, for *just* the auto tiling layouts, we need a tile store
# that keeps track of which windows are masters and which are slaves...
# The store also says which windows should get which status when
# appropriate. Secondly, we need a grid structure that is available
# to any tiling layout--but is the horsepower of the manual tiler.
# i.e., The grid would be helpful in auto layouts like Vertical
# or Horizontal, but not cascade.
