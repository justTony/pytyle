import ptxcb
from monitor import Monitor

import xcb.xproto

class Window(object):
    WINDOWS = {}

    def __init__(self, wid):
        self.id = wid
        self._xwin = ptxcb.Window(wid)
        self.load()

    def __str__(self):
        length = 30
        padded_name = ''.join([' ' if ord(c) > 127 else c for c in self.name[0:length].strip()])
        spaces = length - len(padded_name)

        padded_name += ' ' * spaces

        return '%s - [ID: %d, WORKSPACE: %d, MONITOR: %d, X: %d, Y: %d, Width: %d, Height: %d]' % (
            padded_name, self.id, self.monitor.workspace.id, self.monitor.id, self.x, self.y, self.width, self.height
        )

    def maximize(self):
        self._xwin.maximize()

    def moveresize(self, x, y, width, height):
        self._xwin.restore()
        self._xwin.moveresize(x, y, width, height)

    def load(self):
        self.name = self._xwin.get_name()
        self.x, self.y, self.width, self.height = self._xwin.get_geometry()
        self.monitor = Monitor.lookup(self._xwin.get_desktop_number(), self.x, self.y)

    def reload(self):
        self.load()

    def tiling(self):
        win._xwin.set_event_masks(
            xcb.xproto.EventMask.PropertyChange |
            xcb.xproto.EventMask.FocusChange
        )

    def is_manageable(self):
        win_types = self._xwin.get_types()
        if not win_types or '_NET_WM_WINDOW_TYPE_NORMAL' in win_types:
            states = self._xwin.get_states()

            if ('_NET_WM_STATE_MODAL' not in states and
                '_NET_WM_STATE_SHADED' not in states and
                '_NET_WM_STATE_SKIP_TASKBAR' not in states and
                '_NET_WM_STATE_SKIP_PAGER' not in states and
                '_NET_WM_STATE_HIDDEN' not in states and # This omits iconified windows...
                '_NET_WM_STATE_FULLSCREEN' not in states):
                return True
        return False

    @staticmethod
    def lookup(wid):
        if wid in Window.WINDOWS:
            return Window.WINDOWS[wid]
        return None

    @staticmethod
    def deep_lookup(wid):
        ret = Window.lookup(wid)

        if ret:
            return ret

        for child_wid in ptxcb.Window(wid).query_tree_children():
            ret = Window.lookup(child_wid)

            if ret:
                return ret

        return None

    @staticmethod
    def add(wid):
        if wid not in Window.WINDOWS:
            win = Window(wid)

            if win.is_manageable():
                Window.WINDOWS[wid] = win
                return win
        return False

    @staticmethod
    def refresh():
        wids = ptxcb.XROOT.get_window_ids()

        for wid in wids:
            if wid not in Window.WINDOWS:
                win = Window(wid)

                if win.is_manageable():
                    Window.WINDOWS[wid] = win
            else:
                Window.WINDOWS[wid].reload()

        for wid in Window.WINDOWS.keys():
            if wid not in wids:
                #Window.WINDOWS[wid].remove()
                del Window.WINDOWS[wid]

        ptxcb.XCONN.push()
