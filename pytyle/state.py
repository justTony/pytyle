import ptxcb

from window import Window
from monitor import Monitor
from workspace import Workspace

class State(object):
    _singleton = None

    def __init__(self):
        if State._singleton is not None:
            raise State._singleton

        self._ACTIVE = None
        self.pointer_grab = False
        self.moving = False
        self.xinerama = ptxcb.XCONN.xinerama_get_screens()

        self.properties = {
            '_NET_ACTIVE_WINDOW': '',
            '_NET_CLIENT_LIST': set(),
            '_NET_WORKAREA': [],
            '_NET_NUMBER_OF_DESKTOPS': 0,
            '_NET_DESKTOP_GEOMETRY': {},
        }

        self.load_properties()

    @staticmethod
    def get_state():
        if State._singleton is None:
            State._singleton = State()

        return State._singleton

    def update_property(self, pname):
        if pname in self.properties:
            if pname == '_NET_ACTIVE_WINDOW':
                self.refresh_active()
                self.properties[pname] = self.get_active()
            elif pname == '_NET_CLIENT_LIST':
                old = self.properties[pname]
                new = set(ptxcb.XROOT.get_window_ids())

                self.properties[pname] = new

                if old != new:
                    added, removed = self.handle_window_add_or_remove(old, new)
            elif pname == '_NET_WORKAREA':
                self.properties[pname] = ptxcb.XROOT.get_workarea()

                for wsid in Workspace.WORKSPACES:
                    for mid in Workspace.WORKSPACES[wsid].monitors:
                        mon = Workspace.WORKSPACES[wsid].monitors[mid]
                        mon.calculate_workarea()
            elif pname == '_NET_NUMBER_OF_DESKTOPS':
                old = self.properties[pname]
                self.properties[pname] = ptxcb.XROOT.get_number_of_desktops()

                # Add destops...
                if old < self.properties[pname]:
                    for wsid in xrange(old, self.properties[pname]):
                        Workspace.add(wsid)
                        Monitor.add(wsid, self.xinerama)

                # Remove desktops
                elif old > self.properties[pname]:
                    for wsid in xrange(self.properties[pname], old):
                        Monitor.remove(wsid)
                        Workspace.remove(wsid)
            elif pname == '_NET_DESKTOP_GEOMETRY':
                old_geom = self.properties[pname]
                old_xinerama = self.xinerama

                time.sleep(1)

                # Figure out a way to update screens...
                # It's easy if it's just the resolution changing,
                # but what about adding/removing monitors? :-(

                self.properties[pname] = ptxcb.XROOT.get_desktop_geometry()
                self.xinerama = ptxcb.XCONN.xinerama_get_screens()

    def load_properties(self):
        property_order = [
            '_NET_NUMBER_OF_DESKTOPS',
            '_NET_WORKAREA',
            '_NET_CLIENT_LIST',
            '_NET_ACTIVE_WINDOW',
        ]

        for pname in property_order:
            self.update_property(pname)

    def refresh_active(self):
        self.set_active(ptxcb.XROOT.get_active_window())

        active = self.get_active()

        if active:
            active.monitor.active = active

    def set_active(self, wid):
        if wid in Window.WINDOWS:
            self._ACTIVE = Window.WINDOWS[wid]
        else:
            self._ACTIVE = None

    def get_active(self):
        return self._ACTIVE

    def get_active_wsid_and_mid(self):
        wsid = -1
        mid = -1
        win = self.get_active()

        if win:
            wsid = win.monitor.workspace.id
            mid = win.monitor.id
        else:
            px, py = ptxcb.XROOT.get_pointer_position()
            wsid = ptxcb.XROOT.get_current_desktop()

            for m in Monitor.MONITORS[wsid]:
                if Monitor.MONITORS[wsid][m].contains(px, py):
                    mid = m
                    break

        return (wsid, mid)

    def get_active_monitor(self):
        wsid, mid = self.get_active_wsid_and_mid()

        return self.get_monitor(wsid, mid)

    def get_monitor(self, wsid, mid):
        return Monitor.MONITORS[wsid][mid]

    def print_hierarchy(self, workspaces=None, monitors=None):
        if isinstance(workspaces, int):
            workspaces = [workspaces]

        if isinstance(monitors, int):
            monitors = [monitors]

        for wsid in Workspace.WORKSPACES:
            if workspaces is None or wsid in workspaces:
                print Workspace.WORKSPACES[wsid]

                mons = Workspace.WORKSPACES[wsid].monitors
                for mon in mons:
                    if monitors is None or mon.id in monitors:
                        print '\t%s' % mon

                        for win in mon.windows:
                            print '\t\t%s' % win

    def iter_tilers(self, workspaces=None, monitors=None):
        if isinstance(workspaces, int):
            workspaces = [workspaces]

        if isinstance(monitors, int):
            monitors = [monitors]

        for wsid in Workspace.WORKSPACES:
            if workspaces is None or wsid in workspaces:
                mons = Workspace.WORKSPACES[wsid].monitors
                for mid in mons:
                    mon = mons[mid]
                    if monitors is None or mon.id in monitors:
                        tiler = mon.get_tiler()

                        if tiler and tiler.tiling:
                            yield tiler

    def handle_window_add_or_remove(self, old, new):
        added = []
        removed = []

        for wid in new.difference(old):
            win = Window.add(wid)

            if win:
                added.append(win)

        for wid in old.difference(new):
            win = Window.remove(wid)

            if win:
                removed.append(win)

        return added, removed

STATE = State.get_state()
