import ptxcb
from workspace import Workspace

class Monitor(object):
    MONITORS = {}

    def __init__(self, workspace, mid, x, y, width, height):
        self.workspace = workspace
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

    def __str__(self):
        return 'Monitor %d - [WORKSPACE: %d, X: %d, Y: %d, Width: %d, Height: %d]' % (
            self.id, self.workspace.id, self.x, self.y, self.width, self.height
        )

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
            geom = win.get_geometry()

            if self.workspace.contains(win.get_desktop_number()) and self.contains(geom[0], geom[1]):
                struts = win.get_strut_partial()
                if not struts:
                    struts = win.get_strut()

                if struts:
                    self.workspace.id, self.id, win.get_visible_name(), struts, '\n'

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
