import traceback, sys, time

import xcb.xproto, xcb.xcb

import pytyle.ptxcb as ptxcb
from pytyle.command import Command
from pytyle.state import STATE
from pytyle.window import Window
from pytyle.dispatcher import Dispatcher

cmds = {
    'Alt-Shift-Return': 'list-windows-by-id',
    'Alt-Z': 'list-windows-by-name',
    'Ctrl-C': 'quit',
    'Alt-A': 'tile',
}

Command.init(cmds)

STATE.refresh()

ptxcb.XCONN.push()

while True:
    try:
        event_data = ptxcb.event.dispatch(
            ptxcb.XCONN.get_conn().wait_for_event()
        )
    except xcb.xproto.BadAccess, error:
        print error
        break

    if not event_data:
        continue

    d = Dispatcher(event_data)

    ptxcb.XCONN.push()

    ptxcb.Window.exec_queue()

    if d.stop():
        break

ptxcb.XCONN.disconnect()
