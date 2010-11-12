import traceback, sys, time

import xcb.xproto, xcb.xcb

import pytyle.config as config
import pytyle.ptxcb as ptxcb
import pytyle.state as state
from pytyle.command import Command
from pytyle.dispatcher import Dispatcher

Command.init()

state.apply_config()

while True:
    try:
        event_data = ptxcb.event.dispatch(
            ptxcb.connection.conn.wait_for_event()
        )
    except xcb.xproto.BadWindow, error:
        continue
    except xcb.xproto.BadAccess, error:
        print error
        break

    if not event_data:
        continue

    d = Dispatcher(event_data)

    if d.stop():
        break

ptxcb.connection.disconnect()
