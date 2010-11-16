import math

from pytyle.tile_auto import AutoTile

class Cascade(AutoTile):
    def __init__(self, monitor):
        AutoTile.__init__(self, monitor)

        self.hsplit = self.get_option('width_factor')
        self.vsplit = self.get_option('height_factor')

    def tile(self):
        AutoTile.tile(self)

        m_size = len(self.store.masters)
        s_size = len(self.store.slaves)

        if not m_size and not s_size:
            return

        push_down = self.get_option('push_down')
        push_over = self.get_option('push_over')
        if self.get_option('horz_align') == 'right':
            push_over = -push_over

        m_width = int(
            self.monitor.wa_width * self.hsplit - push_over * s_size
        )
        m_height = int(
            self.monitor.wa_height * self.vsplit - push_down * s_size
        )
        m_y = self.monitor.wa_y + push_down * s_size

        s_width = int(self.monitor.wa_width * self.hsplit)
        s_height = int(self.monitor.wa_height * self.vsplit)
        s_y = self.monitor.wa_y

        if (
            m_width <= 0 or m_width > self.monitor.wa_width or
            s_width <= 0 or s_width > self.monitor.wa_width or
            m_height <= 0 or m_height > self.monitor.wa_height or
            s_height <= 0 or s_height > self.monitor.wa_height
        ):
            self.error_exec_callbacks()
            return

        if self.get_option('horz_align') == 'right':
            m_x = (
                self.monitor.wa_x +
                (self.monitor.wa_width - m_width) +
                (push_over * s_size)
            )
            s_x = self.monitor.wa_x + (self.monitor.wa_width - s_width)
        else:
            m_x = self.monitor.wa_x + (push_over * s_size)
            s_x = self.monitor.wa_x

        for i, cont in enumerate(self.store.slaves):
            cont.moveresize(
                s_x + (i * push_over),
                s_y + (i * push_down),
                s_width - (i * push_over),
                s_height - (i * push_down)
            )
            cont.window_raise()

        for i, cont in enumerate(self.store.masters):
            cont.moveresize(
                m_x,
                m_y,
                m_width,
                m_height
            )
            cont.window_raise()

        self._raise_active()

        # If we've made it this far, then we've supposedly tiled correctly
        self.error_clear()

    def _raise_active(self):
        active = self._get_active()
        if active:
            active.window_raise()

    def _restack(self):
        for cont in self.store.slaves:
            cont.window_raise()

        for cont in self.store.masters:
            cont.window_raise()

    def decrement_hsplit(self):
        self.hsplit -= self.get_option('step_size')

    def increment_hsplit(self):
        self.hsplit += self.get_option('step_size')

    def decrement_vsplit(self):
        self.vsplit -= self.get_option('step_size')

    def increment_vsplit(self):
        self.vsplit += self.get_option('step_size')

    def decrease_master(self):
        self.decrement_hsplit()
        self.decrement_vsplit()

        self.error_register_callback(self.increment_hsplit)
        self.error_register_callback(self.increment_vsplit)
        self.enqueue()

    def increase_master(self):
        self.increment_hsplit()
        self.increment_vsplit()

        self.error_register_callback(self.decrement_hsplit)
        self.error_register_callback(self.decrement_vsplit)
        self.enqueue()

    def cycle(self):
        AutoTile.cycle(self)
        self._restack()

    def focus_master(self):
        self._restack()
        AutoTile.focus_master(self)

    def make_active_master(self):
        AutoTile.make_active_master(self)
        self._restack()
        self._raise_active()

    def next(self):
        self._restack()
        AutoTile.next(self)

    def previous(self):
        self._restack()
        AutoTile.previous(self)

    def switch_next(self):
        AutoTile.switch_next(self)
        self._restack()
        self._raise_active()

    def switch_previous(self):
        AutoTile.switch_previous(self)
        self._restack()
        self._raise_active()

    def decrement_masters(self):
        pass

    def increment_masters(self):
        pass
