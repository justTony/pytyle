from pytyle.tile_auto import AutoTile

class Vertical(AutoTile):
    def __init__(self, monitor):
        AutoTile.__init__(self, monitor)

        self.hsplit = 0.5

    def tile(self):
        AutoTile.tile(self)

        m_size = len(self.store.masters)
        s_size = len(self.store.slaves)

        m_width = int(self.monitor.wa_width * self.hsplit)
        s_width = self.monitor.wa_width - m_width

        m_x = self.monitor.wa_x
        s_x = m_x + m_width

        if (
            m_width <= 0 or m_width > self.monitor.wa_width or
            s_width <= 0 or s_width > self.monitor.wa_width
        ):
            self.error_exec_callbacks()
            return

        if m_size:
            m_height = self.monitor.wa_height / m_size

            if not s_size:
                m_width = self.monitor.wa_width

            for i, cont in enumerate(self.store.masters):
                cont.moveresize(
                    m_x,
                    self.monitor.wa_y + i * m_height,
                    m_width,
                    m_height
                )

        if s_size:
            s_height = self.monitor.wa_height / s_size

            if not m_size:
                s_width = self.monitor.wa_width
                s_x = self.monitor.wa_x

            for i, cont in enumerate(self.store.slaves):
                cont.moveresize(
                    s_x,
                    self.monitor.wa_y + i * s_height,
                    s_width,
                    s_height
                )

        # If we've made it this far, then we've supposedly tiled correctly
        self.error_clear()

    def decrement_hsplit(self):
        self.hsplit -= self.get_option('step_size')

    def increment_hsplit(self):
        self.hsplit += self.get_option('step_size')

    def decrease_master(self):
        self.decrement_hsplit()

        self.error_register_callback(self.increment_hsplit)
        self.enqueue()

    def increase_master(self):
        self.increment_hsplit()

        self.error_register_callback(self.decrement_hsplit)
        self.enqueue()
