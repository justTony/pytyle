import ptxcb
import tilers
from command import Command
from state import STATE
from window import Window
from tile import Tile

class Dispatcher(object):
    def __init__(self, event_data):
        self._event_data = event_data
        self._stop = False

        assert 'event' in self._event_data

        if hasattr(self, self._event_data['event']):
            getattr(self, self._event_data['event'])()
        else:
            print 'Unrecognized event: %s' % self._event_data['event']
            return

        ptxcb.Window.exec_queue()
        Tile.exec_queue()

        ptxcb.XCONN.push()

    def stop(self):
        return self._stop

    def KeyPressEvent(self):
        cmd = Command.lookup(self._event_data['keycode'], self._event_data['modifiers'])
        x = cmd.get_command()

        if x == 'quit':
            for tiler in STATE.iter_tilers():
                tiler.untile()

            self._stop = True
        elif x == 'debug':
            STATE.print_hierarchy(*STATE.get_active_wsid_and_mid())
        elif x == 'refresh_workarea':
            STATE.update_property('_NET_WORKAREA')
        else:
            Tile.dispatch(STATE.get_active_monitor(), x)

    def ConfigureNotifyEvent(self):
        win = Window.deep_lookup(self._event_data['window'].wid)

        if win and win.lives():
            if win.pytyle_moved:
                win.pytyle_moved = False
            else:
                if STATE.pointer_grab and win.width == self._event_data['width'] and win.height == self._event_data['height']:
                    pointer = ptxcb.XROOT.query_pointer()

                    if ptxcb.XROOT.button_pressed():
                        STATE.moving = win
                        STATE.moving.moving = True

                win.set_geometry(
                    self._event_data['x'],
                    self._event_data['y'],
                    self._event_data['width'],
                    self._event_data['height']
                )

    def PropertyNotifyEvent(self):
        a = self._event_data['atom']

        STATE.update_property(a)

        if self._event_data['window']:
            win = Window.lookup(self._event_data['window'].wid)

            if win and win.lives():
                win.update_property(a)

    def FocusInEvent(self):
        if self._event_data['mode'] == 'Ungrab':
            STATE.pointer_grab = False

            if STATE.moving:
                pointer = ptxcb.XROOT.query_pointer()
                win = Window.deep_lookup(pointer.child)

                if win:
                    for tiler in STATE.iter_tilers(win.monitor.workspace.id):
                        tiler.needs_tiling()

                STATE.moving.moving = False
                STATE.moving = False

    def FocusOutEvent(self):
        if self._event_data['mode'] == 'Grab':
            STATE.pointer_grab = True
