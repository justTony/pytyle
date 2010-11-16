import math

from pytyle.tile_auto import AutoTile

class Center(AutoTile):
    def __init__(self, monitor):
        AutoTile.__init__(self, monitor)

        self.hsplit = self.get_option('width_factor')
        self.vsplit = self.get_option('height_factor')
        self.columns = self.get_option('columns')

    def tile(self):
        AutoTile.tile(self)

        m_size = len(self.store.masters)
        s_size = len(self.store.slaves)

        if not m_size and not s_size:
            return

        rows = int(math.ceil(float(s_size) / float(self.columns)))
        lastrow_columns = s_size % self.columns or self.columns

        m_width = int(self.monitor.wa_width * self.hsplit)
        m_height = int(self.monitor.wa_height * self.vsplit)
        m_x = self.monitor.wa_x + int((self.monitor.wa_width - m_width) / 2)
        m_y = self.monitor.wa_y + int((self.monitor.wa_height - m_height) / 2)

        s_width = int(self.monitor.wa_width / self.columns)
        if not rows:
            s_height = 1
        else:
            s_height = int(self.monitor.wa_height / rows)
        s_x = self.monitor.wa_x
        s_y = self.monitor.wa_y

        if (
            m_width <= 0 or m_width > self.monitor.wa_width or
            s_width <= 0 or s_width > self.monitor.wa_width or
            m_height <= 0 or m_height > self.monitor.wa_height or
            s_height <= 0 or s_height > self.monitor.wa_height
        ):
            self.error_exec_callbacks()
            return

        for i, cont in enumerate(self.store.masters):
            cont.moveresize(
                m_x,
                m_y,
                m_width,
                m_height
            )

        for i, cont in enumerate(self.store.slaves):
            if i / self.columns == rows - 1:
                s_width = self.monitor.wa_width / lastrow_columns

            cont.moveresize(
                s_x + (i % self.columns) * s_width,
                s_y + (i / self.columns) * s_height,
                s_width,
                s_height
            )

        # If we've made it this far, then we've supposedly tiled correctly
        self.error_clear()

    def _lower_master(self):
        for cont in self.store.slaves:
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

    def next(self):
        self._lower_master()
        AutoTile.next(self)

    def previous(self):
        self._lower_master()
        AutoTile.previous(self)

    def decrement_masters(self):
        pass

    def increment_masters(self):
        pass
