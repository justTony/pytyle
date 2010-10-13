# Library imports
import config
import ptxcb
import tilers

# Class imports
from tile import AutoTile
from workspace import Workspace

class Monitor(object):
    @staticmethod
    def add(wsid, xinerama):
        for mid, screen in enumerate(xinerama):
            new_mon = Monitor(
                Workspace.WORKSPACES[wsid],
                mid,
                screen['x'],
                screen['y'],
                screen['width'],
                screen['height']
            )

            Workspace.WORKSPACES[wsid].monitors[mid] = new_mon

    @staticmethod
    def lookup(wsid, x, y):
        if wsid in Workspace.WORKSPACES:
            for mon in Workspace.WORKSPACES[wsid].iter_monitors():
                if mon.contains(x, y):
                    return mon
        return None

    @staticmethod
    def remove(wsid):
        Workspace.WORKSPACES[wsid].monitors = {}

    def __init__(self, workspace, mid, x, y, width, height):
        self.workspace = workspace

        self.id = mid
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.windows = set()
        self.active = None

        self.tiler = None
        self.auto = True
        self.auto_tilers = []
        self.man_tilers = []

        # Attach tilers...
        for tile_name in config.tilers:
            if hasattr(tilers, tile_name):
                tiler = getattr(tilers, tile_name)
                self.add_tiler(tiler(self))

    def add_tiler(self, tiler):
        if isinstance(tiler, AutoTile):
            self.auto_tilers.append(tiler)

    def add_window(self, win):
        self.windows.add(win)

        if win.id == ptxcb.XROOT.get_active_window():
            self.active = win

        if self.tiler:
            self.tiler.add(win)

    def calculate_workarea(self):
        self.wa_x = self.x
        self.wa_y = self.y
        self.wa_width = self.width
        self.wa_height = self.height

        wids = ptxcb.XROOT.get_window_ids()

        for wid in wids:
            win = ptxcb.Window(wid)

            # We're listening to _NET_WORKAREA, so a panel
            # might have died before _NET_CLIENT_LIST was updated...
            try:
                x, y, w, h = win.get_geometry()
            except:
                continue

            if self.workspace.contains(win.get_desktop_number()) and self.contains(x, y):
                struts = win.get_strut_partial()

                if not struts:
                    struts = win.get_strut()

                if struts and not all([struts[i] == 0 for i in struts]):
                    if struts['left'] or struts['right']:
                        if struts['left']:
                            self.wa_x += w
                        self.wa_width -= w

                    if struts['top'] or struts['bottom']:
                        if struts['top']:
                            self.wa_y += h
                        self.wa_height -= h
                elif struts:
                    # When accounting for struts on left/right, and
                    # struts are reported properly, x shouldn't be
                    # zero. Similarly for top/bottom and y.

                    if x > 0 and self.width == (x + w):
                        self.wa_width -= w
                    elif y > 0 and self.height == (y + h):
                        self.wa_height -= h
                    elif x > 0 and self.wa_x == x:
                        self.wa_x += w
                        self.wa_width -= w
                    elif y > 0 and self.wa_y == y:
                        self.wa_y += h
                        self.wa_height -= h

        if self.tiler:
            self.tiler.needs_tiling()

    def contains(self, x, y):
        if x >= self.x and y >= self.y and x < (self.x + self.width) and y < (self.y + self.height):
            return True

        if (x < 0 or y < 0) and self.x == 0 and self.y == 0:
            return True

        return False

    def get_active(self):
        if not self.active:
            if self.windows:
                self.active = [w for w in self.windows][0]

        return self.active

    def get_tiler(self):
        if not self.tiler:
            if self.auto and self.auto_tilers:
                self.tiler = self.auto_tilers[0]
            elif self.man_tilers:
                self.tiler = self.man_tilers[0]

        return self.tiler

    def iter_windows(self):
        for win in self.windows:
            yield win

    def refresh_bounds(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

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

    def __str__(self):
        return 'Monitor %d - [WORKSPACE: %d, X: %d, Y: %d, Width: %d, Height: %d]' % (
            self.id, self.workspace.id, self.x, self.y, self.width, self.height
        )
