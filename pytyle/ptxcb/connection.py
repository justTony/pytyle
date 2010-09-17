import struct

import xcb.xproto, xcb.xcb, xcb.xinerama

class Connection(object):
    _singleton = None

    def __init__(self):
        if Connection._singleton is not None:
            raise Connection._singleton

        self._conn = xcb.xcb.connect()
        self._setup = self._conn.get_setup()

        self._syms_to_codes = {}
        self._codes_to_syms = {}
        self._init_keymap()

    @staticmethod
    def get_connection():
        if Connection._singleton is None:
            Connection._singleton = Connection()

        return Connection._singleton

    def disconnect(self):
        self.get_conn().disconnect()
        Connection._singleton = None

    def flush(self):
        self.get_conn().flush()

    def get_conn(self):
        return self._conn

    def get_core(self):
        return self.get_conn().core

    def get_setup(self):
        return self._setup

    def get_keycode(self, keysym):
        return self._syms_to_codes[keysym]

    def get_keysym(self, keycode):
        return self._codes_to_syms[keycode][0]

    def xinerama_get_screens(self):
        screens = self.get_conn()(xcb.xinerama.key).QueryScreens().reply().screen_info
        ret = []

        for screen in screens:
            ret.append({
                'x': screen.x_org,
                'y': screen.y_org,
                'width': screen.width,
                'height': screen.height
            })

        return ret

    def _init_keymap(self):
        q = self.get_core().GetKeyboardMapping(
            self.get_setup().min_keycode,
            self.get_setup().max_keycode - self.get_setup().min_keycode + 1
        ).reply()

        kpc = q.keysyms_per_keycode

        for i, v in enumerate(q.keysyms):
            keycode = (i / kpc) + self.get_setup().min_keycode

            if v not in self._syms_to_codes:
                self._syms_to_codes[v] = keycode

            if keycode not in self._codes_to_syms:
                self._codes_to_syms[keycode] = []
            self._codes_to_syms[keycode].append(v)

    def xsync(self):
        self.get_core().GetInputFocus().reply()

    def push(self):
        self.flush()
        self.xsync()

XCONN = Connection.get_connection()
