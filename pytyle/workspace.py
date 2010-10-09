import ptxcb

class Workspace(object):
    WORKSPACES = {}

    def __init__(self, wsid, x, y, width, height, total_width, total_height):
        self.id = wsid
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.total_width = total_width
        self.total_height = total_height

        self.monitors = {}

    def __str__(self):
        return 'Workspace %d - [X: %d, Y: %d, Width: %d, Height: %d]' % (
            self.id, self.x, self.y, self.width, self.height
        )

    def contains(self, wsid):
        if wsid == 'all' or self.id == wsid:
            return True
        return False

    def get_monitor(self, mid):
        return self.monitors[mid]

    def has_monitor(self, mid):
        return mid in self.monitors

    @staticmethod
    def add(wsid):
        Desktop.add(wsid)

    @staticmethod
    def remove(wsid):
        Desktop.remove(wsid)

class Desktop(Workspace):
    @staticmethod
    def add(wsid):
        geom = ptxcb.XROOT.get_desktop_geometry()
        wa = ptxcb.XROOT.get_workarea()

        Desktop.WORKSPACES[wsid] = Desktop(
            wsid,
            wa[wsid]['x'],
            wa[wsid]['y'],
            wa[wsid]['width'],
            wa[wsid]['height'],
            geom['width'],
            geom['height']
        )

    @staticmethod
    def remove(wsid):
        del Workspace.WORKSPACES[wsid]

class Viewport(Workspace):
    def __init__(self):
        pass
