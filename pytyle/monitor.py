import ptxcb
from workspace import Workspace

class Monitor(object):
    MONITORS = {}

    def __init__(self, workspace, mid, x, y, width, height):
        self.workspace = workspace
        self.workspace.monitors.add(self)

        self.id = mid
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.wa_x = self.x
        self.wa_y = self.y
        self.wa_width = self.width
        self.wa_height = self.height

        self._calculate_workarea()

        self.windows = set()
        self.tiler = None
        self.active = None

    def get_active(self):
        if not self.active:
            if self.windows:
                self.active = [w for w in self.windows][0]

        return self.active

    def add_window(self, win):
        self.windows.add(win)

        if win.id == ptxcb.XROOT.get_active_window():
            self.active = win

        if self.tiler:
            self.tiler.add(win)

    def remove_window(self, win):
        if win in self.windows:
            self.windows.remove(win)

        if self.active == win:
            if self.windows:
                self.active = [w for w in self.windows][0]
            else:
                self.active = None

        if self.tiler:
            self.tiler.remove(win)

    def contains(self, x, y):
        if x >= self.x and y >= self.y and x < (self.x + self.width) and y < (self.y + self.height):
            return True

        if (x < 0 or y < 0) and self.x == 0 and self.y == 0:
            return True

        return False

    def _calculate_workarea(self):
        wids = ptxcb.XROOT.get_window_ids()

        for wid in wids:
            win = ptxcb.Window(wid)
            x, y, w, h = win.get_geometry()

            if self.workspace.contains(win.get_desktop_number()) and self.contains(x, y):
                struts = win.get_strut_partial()

                if not struts:
                    struts = win.get_strut()

                if struts and not all([x == 0 for x in struts]):
                    if struts['left'] or struts['right']:
                        if struts['left']:
                            self.wa_x -= w
                        self.wa_width -= w

                    if struts['top'] or struts['bottom']:
                        if struts['top']:
                            self.wa_y -= h
                        self.wa_height -= h

    def __str__(self):
        return 'Monitor %d - [WORKSPACE: %d, X: %d, Y: %d, Width: %d, Height: %d]' % (
            self.id, self.workspace.id, self.x, self.y, self.width, self.height
        )

    @staticmethod
    def lookup(wsid, x, y):
        if wsid in Monitor.MONITORS:
            for mid in Monitor.MONITORS[wsid]:
                if Monitor.MONITORS[wsid][mid].contains(x, y):
                    return Monitor.MONITORS[wsid][mid]
        return None

    # Remember, each monitor must be attached to
    # EVERY workspace
    @staticmethod
    def refresh():
        Monitor.MONITORS = {}

        sinfo = ptxcb.XCONN.xinerama_get_screens()

        for wsid in Workspace.WORKSPACES:
            Monitor.MONITORS[wsid] = {}

            for mid, screen in enumerate(sinfo):
                Monitor.MONITORS[wsid][mid] = Monitor(
                    Workspace.WORKSPACES[wsid],
                    mid,
                    screen['x'],
                    screen['y'],
                    screen['width'],
                    screen['height']
                )
