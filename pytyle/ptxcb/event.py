import xcb.xproto

from window import Window
from window import XROOT
from atom import Atom

def dispatch(e):
    NotifyModes = {
        0: 'Normal', 1: 'Grab', 2: 'Ungrab', 'WhileGrabbed': 3
    }

    if isinstance(e, xcb.xproto.KeyPressEvent):
        return {
            'event': 'KeyPressEvent',
            'keycode': e.detail,
            'modifiers': e.state
        }

    elif isinstance(e, xcb.xproto.ButtonPressEvent):
        print 'detail:', e.detail
        print 'root_x:', e.root_x
        print 'root_y:', e.root_y
        print 'event_x:', e.event_x
        print 'event_y:', e.event_y
        print 'state:', e.state
        print 'root:', e.root
        print 'event:', e.event
        print 'child:', e.child

        return {
            'event': 'ButtonPressEvent',
        }

    elif isinstance(e, xcb.xproto.ConfigureNotifyEvent):
        return {
            'event': 'ConfigureNotifyEvent',
            'ewin': Window(e.event) if e.event != XROOT.wid else XROOT,
            'window': Window(e.window),
            'above': Window(e.above_sibling),
            'x': e.x,
            'y': e.y,
            'width': e.width,
            'height': e.height,
        }

    elif isinstance(e, xcb.xproto.PropertyNotifyEvent):
        return {
            'event': 'PropertyNotifyEvent',
            'window': Window(e.window),
            'atom': Atom.get_atom_name(e.atom),
            'state': e.state
        }

    elif isinstance(e, xcb.xproto.FocusInEvent):
        return {
            'event': 'FocusInEvent',
            'window': Window(e.event),
            'detail': e.detail,
            'mode': NotifyModes[e.mode]
        }

    elif isinstance(e, xcb.xproto.FocusOutEvent):
        return {
            'event': 'FocusOutEvent',
            'window': Window(e.event),
            'detail': e.detail,
            'mode': NotifyModes[e.mode]
        }

    elif isinstance(e, xcb.xproto.CreateNotifyEvent):
        return {
            'event': 'CreateNotifyEvent',
            'window': Window(e.window),
            'x': e.x,
            'y': e.y,
            'width': e.width,
            'height': e.height
        }

    # print '-' * 30
    # print e
    # print dir(e)
    # print '-' * 30
