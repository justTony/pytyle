import struct, traceback

import xcb.xproto, xcb.xcb

from atom import Atom
from connection import XCONN
from events import events

class Window(object):
    queue = []

    @staticmethod
    def exec_queue():
        for tup in Window.queue:
            tup[0](*tup[1:])
        Window.queue = []

    def __init__(self, wid):
        self.wid = wid
        self._box = {
            'htop': None, 'hbot': None,
            'vleft': None, 'vright': None
        }

    def listen(self):
        self.set_event_masks(
            xcb.xproto.EventMask.PropertyChange |
            xcb.xproto.EventMask.FocusChange
        )

    def unlisten(self):
        self.set_event_masks(0)

    def query_pointer(self):
        return XCONN.get_core().QueryPointer(self.wid).reply()

    def button_pressed(self):
        pointer = self.query_pointer()

        if xcb.xproto.KeyButMask.Button1 & pointer.mask:
            return True
        return False

    def query_tree_parent(self):
        try:
            return Window(XCONN.get_core().QueryTree(self.wid).reply().parent)
        except:
            return False

    def query_tree_children(self):
        try:
            children = XCONN.get_core().QueryTree(self.wid).reply().children

            return [wid for wid in children]
        except:
            return False

    def activate(self):
        XCONN.get_core().SetInputFocus(0, self.wid, 0)
        self.stack(True)

    def get_name(self):
        return self.get_property('_NET_WM_NAME')

    def get_visible_name(self):
        return self.get_property('_NET_WM_VISIBLE_NAME')

    def get_desktop_number(self):
        ret = self.get_property('_NET_WM_DESKTOP')[0]

        if ret == 0xFFFFFFFF:
            return 'all'

        return ret

    def get_types(self):
        return set([Atom.get_atom_name(anum) for anum in self.get_property('_NET_WM_WINDOW_TYPE')])

    def get_states(self):
        return set([Atom.get_atom_name(anum) for anum in self.get_property('_NET_WM_STATE')])

    def get_allowed_actions(self):
        return set([Atom.get_atom_name(anum) for anum in self.get_property('_NET_WM_ALLOWED_ACTIONS')])

    def get_strut(self):
        raw = self.get_property('_NET_WM_STRUT')

        if not raw:
            return None

        return {
            'left': raw[0],
            'right': raw[1],
            'top': raw[2],
            'bottom': raw[3]
        }

    def get_strut_partial(self):
        raw = self.get_property('_NET_WM_STRUT_PARTIAL')

        if not raw:
            return None

        return {
            'left': raw[0], 'right': raw[1],
            'top': raw[2], 'bottom': raw[3],
            'left_start_y': raw[4], 'left_end_y': raw[5],
            'right_start_y': raw[6], 'right_end_y': raw[7],
            'top_start_x': raw[8], 'top_end_x': raw[9],
            'bottom_start_x': raw[10], 'bottom_end_x': raw[11]
        }

    def get_user_time(self):
        return self.get_property('_NET_WM_USER_TIME')[0]

    def get_frame_extents(self):
        raw = self.get_property('_NET_FRAME_EXTENTS')

        if raw:
            return {
                'left': raw[0],
                'right': raw[1],
                'top': raw[2],
                'bottom': raw[3]
            }
        else:
            return {
                'left': 0, 'right': 0,
                'top': 0, 'bottom': 0
            }

    def maximize(self):
        self.send_client_event(
            Atom.get_atom('_NET_WM_STATE'),
            [
                1, # _NET_WM_STATE_REMOVE = 0, _NET_WM_STATE_ADD = 1, _NET_WM_STATE_TOGGLE = 2
                Atom.get_atom('_NET_WM_STATE_MAXIMIZED_VERT'),
                Atom.get_atom('_NET_WM_STATE_MAXIMIZED_HORZ')
            ]
        )

        XCONN.push()

    def restore(self):
        self.send_client_event(
            Atom.get_atom('_NET_WM_STATE'),
            [
                0, # _NET_WM_STATE_REMOVE = 0, _NET_WM_STATE_ADD = 1, _NET_WM_STATE_TOGGLE = 2
                Atom.get_atom('_NET_WM_STATE_MAXIMIZED_VERT'),
                Atom.get_atom('_NET_WM_STATE_MAXIMIZED_HORZ')
            ]
        )

        XCONN.push()

    def send_to_desktop(self, desktop_num):
        self.send_client_event(Atom.get_atom('_NET_WM_DESKTOP'), [desktop_num])

    def restack(self):
        self.send_client_event(
            Atom.get_atom('_NET_RESTACK_WINDOW'),
            [
                2,
                self.wid,
                0
            ]
        )

    def stack(self, above):
        try:
            XCONN.get_core().ConfigureWindow(
                self.wid,
                xcb.xproto.ConfigWindow.StackMode,
                [xcb.xproto.StackMode.Above if above else xcb.xproto.StackMode.Below]
            )
        except:
            return False

    def get_raw_geometry(self):
        try:
            raw = XCONN.get_core().GetGeometry(self.wid).reply()

            return (raw.x, raw.y, raw.width, raw.height)
        except:
            return False

    def get_geometry(self):
        try:
            rx, ry, rwidth, rheight = self.query_tree_parent().get_raw_geometry()

            return (
                rx,
                ry,
                rwidth,
                rheight
            )

            # rx, ry, rwidth, rheight = self.get_raw_geometry()
            # rawtrans = XCONN.get_core().TranslateCoordinates(self.wid, XROOT.wid, rx, ry).reply()
    #
            # return (
                # rawtrans.dst_x - (2 * rx),
                # rawtrans.dst_y - (2 * ry),
                # rwidth,
                # rheight
            # )
        except:
            return False

    def moveresize(self, x, y, width, height):
        Window.queue.append(
            (Window._moveresize, self, x, y, width, height)
        )

    def _moveresize(self, x, y, width, height):
        try:
            # I might be able to move this elsewhere...
            # Doesn't need to be calculated every time,
            # just when decorations are toggled
            # Also, does it work in other WM's besides Openbox?
            rx, ry, rwidth, rheight = self.get_raw_geometry()
            px, py, pwidth, pheight = self.query_tree_parent().get_raw_geometry()

            w = width - (pwidth - rwidth)
            h = height - (pheight - rheight)

            x = 0 if x < 0 else x
            y = 0 if y < 0 else y
            w = 1 if w <= 0 else w
            h = 1 if h <= 0 else h

            # XCONN.get_core().ConfigureWindow(
                # self.wid,
                # xcb.xproto.ConfigWindow.X | xcb.xproto.ConfigWindow.Y | xcb.xproto.ConfigWindow.Width | xcb.xproto.ConfigWindow.Height,
                # [x, y, w, h]
            # )

            self.send_client_event(
                Atom.get_atom('_NET_MOVERESIZE_WINDOW'),
                [
                    xcb.xproto.Gravity.NorthWest | 1 << 8 | 1 << 9 | 1 << 10 | 1 << 11 | 1 << 13,
                    x,
                    y,
                    w,
                    h
                ],
                32,
                xcb.xproto.EventMask.StructureNotify
            )

            XCONN.push()
        except:
            return False

    def close(self):
        self.send_client_event(
            Atom.get_atom('_NET_CLOSE_WINDOW'),
            [
                xcb.xproto.Time.CurrentTime,
                2,
                0,
                0,
                0
            ]
        )

    def add_decorations(self):
        self.send_client_event(
            Atom.get_atom('_NET_WM_STATE'),
            [
                0,
                Atom.get_atom('_OB_WM_STATE_UNDECORATED')
            ]
        )

        XCONN.push()

    def remove_decorations(self):
        self.send_client_event(
            Atom.get_atom('_NET_WM_STATE'),
            [
                1,
                Atom.get_atom('_OB_WM_STATE_UNDECORATED')
            ]
        )

        XCONN.push()

    def box(self):
        geom = self.get_geometry()

        bw = 5

        self._box['htop'] = LineWindow(geom['x'], geom['y'], geom['width'], bw)
        self._box['hbot'] = LineWindow(geom['x'], geom['y'] + geom['height'], geom['width'] + bw, bw)
        self._box['vleft'] = LineWindow(geom['x'], geom['y'], bw, geom['height'])
        self._box['vright'] = LineWindow(geom['x'] + geom['width'], geom['y'], bw, geom['height'])

    def unbox(self):
        for box in self._box.values():
            box.close()

    def get_property(self, atom_name):
        try:
            rsp = XCONN.get_core().GetProperty(
                False,
                self.wid,
                Atom.get_atom(atom_name),
                Atom.get_atom_type(atom_name),
                0,
                (2 ** 32) - 1
            ).reply()

            if not Atom.get_type_name(atom_name):
                return ''

            if Atom.get_type_name(atom_name) == 'UTF8_STRING':
                return Atom.ords_to_str(rsp.value)
            elif Atom.get_type_name(atom_name) == 'UTF8_STRING[]':
                return Atom.null_terminated_to_strarray(rsp.value)
            else:
                return list(struct.unpack('I' * (len(rsp.value) / 4), rsp.value.buf()))
        except:
            pass

    def send_client_event(self, message_type, data, format=32, event_mask=xcb.xproto.EventMask.SubstructureRedirect):
        XROOT.send_event(self.wid, message_type, data, format, event_mask)

    def send_event(self, to_wid, message_type, data, format=32, event_mask=xcb.xproto.EventMask.SubstructureRedirect):
        try:
            data = data + ([0] * (5 - len(data)))
            packed = struct.pack(
                'BBH7I',
                events['ClientMessageEvent'],
                format,
                0,
                to_wid,
                message_type,
                data[0], data[1], data[2], data[3], data[4]
            )

            XCONN.get_core().SendEvent(
                False,
                self.wid,
                event_mask,
                packed
            )
        except:
            print traceback.format_exc()

    def set_event_masks(self, event_masks):
        try:
            XCONN.get_core().ChangeWindowAttributes(
                self.wid,
                xcb.xproto.CW.EventMask,
                [event_masks]
            )
        except:
            print traceback.format_exc()

    def grab_key(self, key, modifiers):
        try:
            addmods = [
                0,
                xcb.xproto.ModMask.Lock,
                xcb.xproto.ModMask._2,
                xcb.xproto.ModMask._2 | xcb.xproto.ModMask.Lock
            ]

            for mod in addmods:
                XCONN.get_core().GrabKey(
                    True,
                    self.wid,
                    modifiers | mod,
                    key,
                    xcb.xproto.GrabMode.Async,
                    xcb.xproto.GrabMode.Async
                )
        except:
            print traceback.format_exc()
            print 'Could not grab key:', modifiers, '---', key

    def ungrab_key(self, key, modifiers):
        try:
            addmods = [
                0,
                xcb.xproto.ModMask.Lock,
                xcb.xproto.ModMask._2,
                xcb.xproto.ModMask._2 | xcb.xproto.ModMask.Lock
            ]

            for mod in addmods:
                XCONN.get_core().UngrabKey(
                    key,
                    self.wid,
                    modifiers | mod,
                )
        except:
            print traceback.format_exc()
            print 'Could not ungrab key:', modifiers, '---', key

    def grab_button(self, key, modifiers=xcb.xproto.ModMask.Any):
        try:
            XCONN.get_core().GrabButton(
                True,
                self.wid,
                xcb.xproto.EventMask.ButtonPress,
                xcb.xproto.GrabMode.Async,
                xcb.xproto.GrabMode.Async,
                0,
                0,
                key,
                modifiers
            )
        except:
            print traceback.format_exc()
            print 'Could not grab button:', modifiers, '---', key

    # Not currently used
    def set_property(self, atom_name, value):
        try:
            if isinstance(value, list):
                data = struct.pack(len(value) * 'I', *value)
                data_len = len(value)
            else:
                data_len = len(value)
                data = value

            XCONN.get_conn().core.ChangeProperty(
                xcb.xproto.PropMode.Replace,
                self.wid,
                Atom.get_atom(atom_name),
                Atom.get_atom_type(atom_name),
                Atom.get_atom_length(atom_name),
                data_len,
                data
            )
        except:
            print traceback.format_exc()

class LineWindow(Window):
    def __init__(self, x, y, width, height):
        self._root_depth = XCONN.get_setup().roots[0].root_depth
        self._root_visual = XCONN.get_setup().roots[0].root_visual
        self._pixel = XCONN.get_setup().roots[0].black_pixel

        self.wid  = XCONN.get_conn().generate_id()

        XCONN.get_core().CreateWindow(
            self._root_depth,
            self.wid,
            XROOT.wid,
            x,
            y,
            width,
            height,
            0,
            xcb.xproto.WindowClass.InputOutput,
            self._root_visual,
            xcb.xproto.CW.BackPixel,
            [self._pixel]
        )

        self.set_property('_NET_WM_NAME', 'Internal PyTyle Window')
        self.set_property('_NET_WM_WINDOW_TYPE', [Atom.get_atom('_NET_WM_WINDOW_TYPE_NORMAL')])
        self.set_property('_NET_WM_STATE', [
            Atom.get_atom('_OB_WM_STATE_UNDECORATED'),
            Atom.get_atom('_NET_WM_STATE_SKIP_TASKBAR'),
            Atom.get_atom('_NET_WM_STATE_SKIP_PAGER'),
            Atom.get_atom('_NET_WM_STATE_ABOVE'),
            Atom.get_atom('_NET_WM_STATE_HIDDEN')
        ])

        XCONN.get_core().MapWindow(self.wid)
        self.moveresize(x, y, width, height)

        self.send_client_event(
            Atom.get_atom('_NET_WM_STATE'),
            [
                0,
                Atom.get_atom('_NET_WM_STATE_HIDDEN')
            ]
        )

        XCONN.push()

    def close(self):
        XCONN.get_core().UnmapWindow(self.wid)

class RootWindow(Window):
    _singleton = None

    def __init__(self):
        if RootWindow._singleton is not None:
            raise RootWindow._singleton

        self.wid = XCONN.get_setup().roots[0].root
        Atom.build_cache()
        self.windows = set()

        self.listen()

    def listen(self):
        self.set_event_masks(
            xcb.xproto.EventMask.SubstructureNotify |
            xcb.xproto.EventMask.PropertyChange
        )

    @staticmethod
    def get_root_window():
        if RootWindow._singleton is None:
            RootWindow._singleton = RootWindow()

        return RootWindow._singleton

    def get_name(self):
        return 'ROOT'

    def get_visible_name(self):
        return self.get_name()

    def get_supported_hints(self):
        return [Atom.get_atom_name(anum) for anum in self.get_property('_NET_SUPPORTED')]

    def get_window_ids(self):
        self.windows = set(self.get_property('_NET_CLIENT_LIST'))
        return self.windows

    def get_number_of_desktops(self):
        return self.get_property('_NET_NUMBER_OF_DESKTOPS')[0]

    def get_desktop_geometry(self):
        raw = self.get_property('_NET_DESKTOP_GEOMETRY')

        return {
            'width': raw[0],
            'height': raw[1]
        }

    def get_desktop_viewport(self):
        return self.get_property('_NET_DESKTOP_VIEWPORT')

    def get_current_desktop(self):
        return self.get_property('_NET_CURRENT_DESKTOP')[0]

    def get_desktop_names(self):
        return self.get_property('_NET_DESKTOP_NAMES')

    def get_active_window(self):
        return self.get_property('_NET_ACTIVE_WINDOW')[0]

    def get_workarea(self):
        raw = self.get_property('_NET_WORKAREA')
        ret = []

        for i in range(len(raw) / 4):
            i *= 4
            ret.append({
                'x': raw[i + 0],
                'y': raw[i + 1],
                'width': raw[i + 2],
                'height': raw[i + 3]
            })

        return ret

    def get_window_manager_name(self):
        return Window(self.get_property('_NET_SUPPORTING_WM_CHECK')[0]).get_name()

    def get_desktop_layout(self):
        raw = self.get_property('_NET_DESKTOP_LAYOUT')

        return {
            # _NET_WM_ORIENTATION_HORZ = 0
            # _NET_WM_ORIENTATION_VERT = 1
            'orientation': raw[0],
            'columns': raw[1],
            'rows': raw[2],

            # _NET_WM_TOPLEFT = 0, _NET_WM_TOPRIGHT = 1
            # _NET_WM_BOTTOMRIGHT = 2, _NET_WM_BOTTOMLEFT = 3
            'starting_corner': raw[3]
        }

    def is_showing_desktop(self):
        if self.get_property('_NET_SHOWING_DESKTOP')[0] == 1:
            return True
        return False

    def get_pointer_position(self):
        raw = self.query_pointer()

        return (raw.root_x, raw.root_y)

XROOT = RootWindow.get_root_window()
