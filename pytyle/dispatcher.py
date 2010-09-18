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

    def stop(self):
        return self._stop

    def KeyPressEvent(self):
        cmd = Command.lookup(self._event_data['keycode'], self._event_data['modifiers'])

        if cmd.get_command() == 'quit':
            self._stop = True
        else:
            Tile.dispatch(tilers.Vertical, cmd.get_command())

    def ConfigureNotifyEvent(self):
        pass
        #~ print '-' * 30
        #~ print 'ConfigureNotify'
        #~ print 'Root?', self._event_data['ewin'].wid
        #~ print 'Window:', hex(self._event_data['window'].wid), self._event_data['window'].get_visible_name()
        #~ qtree = ptxcb.XCONN.get_core().QueryTree(self._event_data['window'].wid).reply()
#~
        #~ for c in qtree.children:
            #~ win = Window.lookup(c)
            #~ if win:
                #~ print win.name
#~
        #~ print 'x, y:', self._event_data['x'], self._event_data['y']
        #~ print 'w, h:', self._event_data['width'], self._event_data['height']
        #~ print '-' * 30

    def PropertyNotifyEvent(self):
        a = self._event_data['atom']

        if a in ['_NET_WM_USER_TIME', '_NET_WM_ICON_GEOMETRY']:
            return

        #~ print '-' * 30
        #~ print 'PropertyNotify'
        #~ print 'Window:', self._event_data['window'].get_visible_name()
        #~ print 'Atom:', self._event_data['atom']
        #~ print 'New Value:', self._event_data['window'].get_property(self._event_data['atom'])
        #~ print '-' * 30

        if a == '_NET_ACTIVE_WINDOW':
            STATE.refresh_active()

    # Don't register new windows this way... Use _NET_CLIENT_LIST instead
    # You did it the first time for good reason!
    def CreateNotifyEvent(self):
        win = Window.deep_lookup(self._event_data['window'].wid)

        if win:
            print win.name
        else:
            print self._event_data['window'].wid, self._event_data['window'].get_name()


    # Use the following to track window movement..? Hmmm
    # ConfigureNotify doesn't get reported when windows are moved (yes when resized)
    # It is reported for the ROOT window, however there is no way to know
    # which window is being moved... Check out XQueryTree!
    # http://xcb.freedesktop.org/manual/group__XCB____API.html#g4d0136b27bbab9642aa65d2a3edbc03c

    def FocusInEvent(self):
        print '-' * 30
        print 'FocusIn'
        print 'Window:', self._event_data['window'].get_visible_name()
        print 'Detail:', self._event_data['detail']
        print 'Mode:', self._event_data['mode']
        print '-' * 30

    def FocusOutEvent(self):
        print '-' * 30
        print 'FocusOut'
        print 'Window:', self._event_data['window'].get_visible_name()
        print 'Detail:', self._event_data['detail']
        print 'Mode:', self._event_data['mode']
        print '-' * 30
