import time

import ptxcb
from monitor import Monitor

class Window(object):
    WINDOWS = {}

    def __init__(self, wid):
        self.id = wid
        self._xwin = ptxcb.Window(wid)
        self.container = None
        self.monitor = None
        self.floating = False
        self.pytyle_moved = False
        self.moving = False
        self.properties = {
            '_NET_WM_NAME': '',
            '_NET_WM_DESKTOP': '',
            '_NET_WM_WINDOW_TYPE': set(),
            '_NET_WM_STATE': set(),
            '_NET_WM_ALLOWED_ACTIONS': set(),
            '_NET_FRAME_EXTENTS': {
                'top': 0, 'left': 0, 'right': 0, 'bottom': 0
            }
        }

        self.load()

    def update_monitor(self):
        new_mon = Monitor.lookup(self.properties['_NET_WM_DESKTOP'], self.x, self.y)

        if new_mon:
            self.set_monitor(new_mon.workspace.id, new_mon.id)

    def set_monitor(self, wsid, mid, force=False):
        new_mon = Monitor.MONITORS[wsid][mid]

        if new_mon != self.monitor or force:
            if self.monitor and self in self.monitor.windows:
                self.monitor.remove_window(self)

            self.monitor = new_mon
            self.monitor.add_window(self)

    def update_property(self, pname):
        if pname in self.properties:
            if pname == '_NET_WM_NAME':
                self.name = self._xwin.get_name()
                self.properties[pname] = self.name
            elif pname == '_NET_FRAME_EXTENTS':
                if self.container:
                    self.container.fit_window()

                self.properties[pname] = self._xwin.get_frame_extents()
            # This makes the window tile FIRST...
            elif pname == '_NET_WM_DESKTOP':
                self.properties[pname] = self._xwin.get_desktop_number()

                self.load_geometry()
                self.update_monitor()
            elif pname == '_NET_WM_WINDOW_TYPE':
                self.properties[pname] = self._xwin.get_types()
            elif pname == '_NET_WM_STATE':
                old = self.properties[pname]
                new = self._xwin.get_states()

                # Update the property before continuing...
                self.properties[pname] = new

                removed = old - new
                added = new - old

                if self.container:
                    if '_OB_WM_STATE_UNDECORATED' in removed or '_OB_WM_STATE_UNDECORATED' in added:
                        self.container.fit_window()
                    elif '_NET_WM_STATE_HIDDEN' in added:
                        self.container.tiler.remove(self)
                elif self.monitor and self.monitor.tiler and '_NET_WM_STATE_HIDDEN' in removed:
                    time.sleep(0.2)
                    self.monitor.tiler.add(self)
            elif pname == '_NET_WM_ALLOWED_ACTIONS':
                self.properties[pname] = self._xwin.get_allowed_actions()

    def load_properties(self):
        for pname in self.properties:
            self.update_property(pname)

    def get_property(self, pname):
        assert pname in self.properties

        return self.properties[pname]

    def activate(self):
        self._xwin.activate()

    def original_state(self):
        if self.omaximized:
            self.maximize()
        else:
            self._xwin.moveresize(self.ox, self.oy, self.owidth, self.oheight)

    def maximize(self):
        self._xwin.maximize()

    def maximized(self):
        states = self.properties['_NET_WM_STATE']

        if '_NET_WM_STATE_MAXIMIZED_VERT' in states and '_NET_WM_STATE_MAXIMIZED_HORZ' in states:
            return True
        return False

    def moveresize(self, x, y, width, height):
        self.x, self.y, self.width, self.height = x, y, width, height

        self.pytyle_moved = True

        self._xwin.restore()
        self._xwin.moveresize(x, y, width, height)

    def load(self):
        self.load_geometry()
        self.load_properties()
        self.update_monitor()

        self._xwin.listen()

    def load_geometry(self):
        self.x, self.y, self.width, self.height = self._xwin.get_geometry()

    def reload(self):
        self.load()

    def lives(self):
        try:
            self._xwin.get_desktop_number()
            return True
        except:
            return False

    def set_geometry(self, x, y, w, h):
        self.x, self.y, self.width, self.height = x, y, w, h

        self.update_monitor()

    def set_container(self, container):
        self.container = container

        if container:
            self.ox, self.oy, self.owidth, self.oheight = self._xwin.get_geometry()
            self.omaximized = self.maximized()

    def tilable(self):
        if self.floating:
            return False

        states = self.properties['_NET_WM_STATE']
        if '_NET_WM_STATE_HIDDEN' in states:
            return False

        return True

    @staticmethod
    def manageable(wid):
        win = ptxcb.Window(wid)

        win_types = win.get_types()
        if not win_types or '_NET_WM_WINDOW_TYPE_NORMAL' in win_types:
            states = win.get_states()

            if ('_NET_WM_STATE_MODAL' not in states and
                '_NET_WM_STATE_SHADED' not in states and
                '_NET_WM_STATE_SKIP_TASKBAR' not in states and
                '_NET_WM_STATE_SKIP_PAGER' not in states and
                '_NET_WM_STATE_FULLSCREEN' not in states):
                return True
        return False

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
            print 'Bad form Peter...'

        print '-' * 30, '\n'

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
    def add(wid):
        if wid not in Window.WINDOWS:
            if Window.manageable(wid):
                win = Window(wid)
                Window.WINDOWS[wid] = win

                return win
        return None

    @staticmethod
    def remove(wid):
        win = Window.lookup(wid)

        if win:
            del Window.WINDOWS[wid]
            win.monitor.remove_window(win)

            return win
        return None
