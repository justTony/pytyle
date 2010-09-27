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

        self.monitors = set()

    def __str__(self):
        return 'Workspace %d - [X: %d, Y: %d, Width: %d, Height: %d]' % (
            self.id, self.x, self.y, self.width, self.height
        )

    def contains(self, wsid):
        if wsid == 'all' or self.id == wsid:
            return True
        return False

    @staticmethod
    def refresh():
        Desktop.refresh()

class Desktop(Workspace):
    @staticmethod
    def refresh():
        geom = ptxcb.XROOT.get_desktop_geometry()
        ndesks = ptxcb.XROOT.get_number_of_desktops()
        wa = ptxcb.XROOT.get_workarea()

        for i in range(ndesks):
            Desktop.WORKSPACES[i] = Desktop(
                i,
                wa[i]['x'],
                wa[i]['y'],
                wa[i]['width'],
                wa[i]['height'],
                geom['width'],
                geom['height']
            )

class Viewport(Workspace):
    def __init__(self):
        pass

    @staticmethod
    def refresh():
        Viewport.WORKSPACES = {'0': None}
