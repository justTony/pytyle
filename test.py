# http://xcb.freedesktop.org/manual/modules.html
# http://xcb.freedesktop.org/XcbPythonBinding/
# http://github.com/cortesi/qtile/blob/master/libqtile/xcbq.py

import struct
import xcb.xproto, xcb.xinerama, xcb.xcb

conn = xcb.xcb.connect()
setup = conn.get_setup()
screen = setup.roots[0]

_NET_CLIENT_LIST = conn.core.InternAtom(False, 16, '_NET_CLIENT_LIST').reply().atom
_NET_WM_NAME = conn.core.InternAtom(False, 12, '_NET_WM_NAME').reply().atom
TYPE_WINDOW = conn.core.InternAtom(False, 6, 'WINDOW').reply().atom

windows_response = conn.core.GetProperty(False, screen.root, _NET_CLIENT_LIST, TYPE_WINDOW, 0, (2**32) - 1).reply()
windows = struct.unpack_from('I' * (len(windows_response.value) / 4), windows_response.value.buf())

print windows

last_win_name = ''.join(chr(i) for i in conn.core.GetProperty(False, windows[-1], _NET_WM_NAME, xcb.xproto.GetPropertyType.Any, 0, (2**32) - 1).reply().value)

print 'Last window name: %s' % last_win_name
