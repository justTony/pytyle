import traceback, sys, time

import xcb.xproto, xcb.xcb

import pytyle.ptxcb as ptxcb
from pytyle.command import Command
from pytyle.state import STATE
from pytyle.window import Window
from pytyle.dispatcher import Dispatcher

cmds = {
    'Alt-M': 'focus_master',
    'Alt-Return': 'make_active_master',
    'Alt-H': 'decrease_master',
    'Alt-L': 'increase_master',
    'Alt-J': 'previous',
    'Alt-K': 'next',
    'Alt-Shift-J': 'switch_previous',
    'Alt-Shift-K': 'switch_next',
    'Alt-C': 'cycle',
    'Alt-comma': 'decrement_masters',
    'Alt-period': 'increment_masters',
    'Alt-E': 'screen0_focus',
    'Alt-W': 'screen1_focus',
    'Alt-R': 'screen2_focus',
    'Alt-Shift-E': 'screen0_put',
    'Alt-Shift-W': 'screen1_put',
    'Alt-Shift-R': 'screen2_put',
    'Alt-Shift-S': 'refresh_workarea',
    'Alt-F': 'float',
    'Alt-Ctrl-C': 'quit',
    'Alt-A': 'tile',
    'Alt-U': 'untile',
    'Alt-Z': 'cycle_tiler',
    'Alt-Shift-space': 'reset',
    'Alt-D': 'debug',
}

Command.init(cmds)

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

    if d.stop():
        break

ptxcb.XCONN.disconnect()
