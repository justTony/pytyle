import ptxcb
from monitor import Monitor

import xcb.xproto

class Window(object):
    WINDOWS = {}

    def __init__(self, wid):
        self.id = wid
        self._xwin = ptxcb.Window(wid)
        self.container = None
        self.load()

    def __str__(self):
        length = 30
        padded_name = ''.join([' ' if ord(c) > 127 else c for c in self.name[0:length].strip()])
        spaces = length - len(padded_name)

        padded_name += ' ' * spaces

        return '%s - [ID: %d, WORKSPACE: %d, MONITOR: %d, X: %d, Y: %d, Width: %d, Height: %d]' % (
            padded_name, self.id, self.monitor.workspace.id, self.monitor.id, self.x, self.y, self.width, self.height
        )

    def sanity_move_resize(self):
        print '-' * 30

        print self.name
        print '-' * 15

        x1, y1, w1, h1 = self._xwin.get_geometry()
        print 'Originals'
        print x1, y1, w1, h1
        print '-' * 15

        self._xwin._moveresize(x1, y1, w1, h1)
        x2, y2, w2, h2 = self._xwin.get_geometry()

        print 'After move/resize'
        print x2, y2, w2, h2
        print '-' * 15

        if x1 == x2 and y1 == y2 and w1 == w2 and h1 == h2:
            print 'EXCELLENT!'
        else:
            print 'Bad form...'

        print '-' * 30, '\n'

    def activate(self):
        self._xwin.activate()

    def original_state(self):
        if self.omaximized:
            self.maximize()
        else:
            self._xwin.moveresize(self.ox, self.oy, self.owidth, self.oheight)

    def maximize(self):
        self._xwin.maximize()

    def moveresize(self, x, y, width, height):
        self.x, self.y, self.width, self.height = x, y, width, height

        self._xwin.restore()
        self._xwin.moveresize(x, y, width, height)

    def load(self):
        self.name = self._xwin.get_name()
        self.load_geometry()
        self.omaximized = self._xwin.maximized()
        self.monitor = Monitor.lookup(self.get_desktop_number(), self.x, self.y)
        self.floating = False

        self._xwin.listen()

    def load_geometry(self):
        self.x, self.y, self.width, self.height = self._xwin.get_geometry()

    def reload(self):
        self.load()

    def lives(self):
        try:
            self.get_desktop_number()
            return True
        except:
            return False

    def get_desktop_number(self):
        return self._xwin.get_desktop_number()

    def set_container(self, container):
        self.container = container

        if container:
            self.ox, self.oy, self.owidth, self.oheight = self._xwin.get_geometry()
            self.omaximized = self._xwin.maximized()

    def tilable(self):
        if self.floating:
            return False

        states = self._xwin.get_states()
        if '_NET_WM_STATE_HIDDEN' in states:
            return False

        return True

    def is_manageable(self):
        win_types = self._xwin.get_types()
        if not win_types or '_NET_WM_WINDOW_TYPE_NORMAL' in win_types:
            states = self._xwin.get_states()

            if ('_NET_WM_STATE_MODAL' not in states and
                '_NET_WM_STATE_SHADED' not in states and
                '_NET_WM_STATE_SKIP_TASKBAR' not in states and
                '_NET_WM_STATE_SKIP_PAGER' not in states and
                # '_NET_WM_STATE_HIDDEN' not in states and # This omits iconified windows...
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

        children = ptxcb.Window(wid).query_tree_children()

        if children:
            for child_wid in children:
                ret = Window.lookup(child_wid)

                if ret:
                    return ret

        return None

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
