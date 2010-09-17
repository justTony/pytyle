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

    @staticmethod
    def get_state():
        if State._singleton is None:
            State._singleton = State()

        return State._singleton

    def refresh_active(self):
        self.set_active(ptxcb.XROOT.get_active_window())

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
        for wsid in self._hierarchy:
            if workspaces is None or wsid in workspaces:
                print Workspace.WORKSPACES[wsid]

                for mid in self._hierarchy[wsid]:
                    if monitors is None or mid in monitors:
                        print '\t%s' % Monitor.MONITORS[wsid][mid]

                        for wid in self._hierarchy[wsid][mid]:
                            print '\t\t%s' % Window.WINDOWS[wid]

    def iter_windows(self, workspaces=None, monitors=None):
        if isinstance(workspaces, int):
            workspaces = [workspaces]

        if isinstance(monitors, int):
            monitors = [monitors]

        for wsid in self._hierarchy:
            if workspaces is None or wsid in workspaces:
                for mid in self._hierarchy[wsid]:
                    if monitors is None or mid in monitors:
                        for wid in self._hierarchy[wsid][mid]:
                            yield Window.WINDOWS[wid]

    def refresh(self):
        Workspace.refresh()
        Monitor.refresh()
        Window.refresh()
        self.refresh_hierarchy()
        self.refresh_active()

        #self.print_hierarchy([2], [1])

    def refresh_hierarchy(self):
        for wsid in Workspace.WORKSPACES:
            self._hierarchy[wsid] = {}

            for mid in Monitor.MONITORS[wsid]:
                self._hierarchy[wsid][mid] = set()

        for wid in Window.WINDOWS:
            win = Window.WINDOWS[wid]
            self._hierarchy[win.monitor.workspace.id][win.monitor.id].add(wid)

STATE = State.get_state()
