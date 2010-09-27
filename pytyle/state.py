import ptxcb

from window import Window
from monitor import Monitor
from workspace import Workspace

class State(object):
    _singleton = None

    def __init__(self):
        if State._singleton is not None:
            raise State._singleton

        # Contains the hierarchical relationship:
        # workspaces -> monitors -> windows
        self._hierarchy = {}
        self._ACTIVE = None
        self.pointer_grab = False
        self.moving = False

    @staticmethod
    def get_state():
        if State._singleton is None:
            State._singleton = State()

        return State._singleton

    def refresh_active(self):
        self.set_active(ptxcb.XROOT.get_active_window())

        active = STATE.get_active()

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

    def iter_windows(self, workspaces=None, monitors=None):
        if isinstance(workspaces, int):
            workspaces = [workspaces]

        if isinstance(monitors, int):
            monitors = [monitors]

        for wsid in Workspace.WORKSPACES:
            if workspaces is None or wsid in workspaces:
                mons = Workspace.WORKSPACES[wsid].monitors
                for mon in mons:
                    if monitors is None or mon.id in monitors:
                        for win in mon.windows:
                            yield win

    def handle_window_add_or_remove(self, old, new):
        added = []
        removed = []

        for wid in new.difference(old):
            win = Window.add_window(wid)

            if win:
                added.append(win)

        for wid in old.difference(new):
            win = Window.remove_window(wid)

            if win:
                removed.append(win)

        return added, removed

    def update_window_position(self, win, x, y, width, height):
        win.x, win.y, win.width, win.height = x, y, width, height

        old = {
            'wsid': win.monitor.workspace.id,
            'mid': win.monitor.id
        }

        new_wsid = win.properties['_NET_WM_DESKTOP']
        new_mon = Monitor.lookup(new_wsid, x, y)
        new_mid = new_mon.id
        new = {
            'wsid': new_wsid,
            'mid': new_mid
        }

        if old != new:
            if win.id in self._hierarchy[win.monitor.workspace.id][win.monitor.id]:
                self._hierarchy[win.monitor.workspace.id][win.monitor.id].remove(win.id)
            self._hierarchy[new_wsid][new_mid].add(win.id)
            win.monitor = new_mon

            return {
                'old': old,
                'new': new
            }
        else:
            return None

    def update_window_desktop(self, win):
        win.load_geometry()

        old = {
            'wsid': win.monitor.workspace.id,
            'mid': win.monitor.id
        }

        new_wsid = win.properties['_NET_WM_DESKTOP']
        new_mon = Monitor.lookup(new_wsid, win.x, win.y)
        new_mid = new_mon.id
        new = {
            'wsid': new_wsid,
            'mid': new_mid
        }

        if old != new:
            self._hierarchy[win.monitor.workspace.id][win.monitor.id].remove(win.id)
            self._hierarchy[new_wsid][new_mid].add(win.id)
            win.monitor = new_mon

            return {
                'old': old,
                'new': new
            }
        else:
            return None


    def refresh(self):
        Workspace.refresh()
        Monitor.refresh()
        Window.refresh()
        self.refresh_active()

    # def refresh_hierarchy(self):
        # for wsid in Workspace.WORKSPACES:
            # self._hierarchy[wsid] = {}
#
            # for mid in Monitor.MONITORS[wsid]:
                # self._hierarchy[wsid][mid] = set()
#
        # for wid in Window.WINDOWS:
            # win = Window.WINDOWS[wid]
            # self._hierarchy[win.monitor.workspace.id][win.monitor.id].add(wid)

STATE = State.get_state()
