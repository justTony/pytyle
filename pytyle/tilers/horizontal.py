from pytyle.tile import AutoTile

class Horizontal(AutoTile):
    def __init__(self, monitor):
        AutoTile.__init__(self, monitor)

        self.vsplit = 0.5

    def tile(self):
        AutoTile.tile(self)

        m_size = len(self.store.masters)
        s_size = len(self.store.slaves)

        m_height = int(self.monitor.wa_height * self.vsplit)
        s_height = self.monitor.wa_height - m_height

        m_y = self.monitor.wa_y
        s_y = m_y + m_height

        if (
            m_height <= 0 or m_height > self.monitor.wa_height or
            s_height <= 0 or s_height > self.monitor.wa_height
        ):
            self.error_exec_callbacks()
            return

        if m_size:
            m_width = self.monitor.wa_width / m_size

            if not s_size:
                m_height = self.monitor.wa_height

            for i, cont in enumerate(self.store.masters):
                cont.moveresize(
                    self.monitor.wa_x + i * m_width,
                    m_y,
                    m_width,
                    m_height
                )

        if s_size:
            s_width = self.monitor.wa_width / s_size

            if not m_size:
                s_height = self.monitor.wa_height
                s_y = self.monitor.wa_y

            for i, cont in enumerate(self.store.slaves):
                cont.moveresize(
                    self.monitor.wa_x + i * s_width,
                    s_y,
                    s_width,
                    s_height
                )

        # If we've made it this far, then we've supposedly tiled correctly
        self.error_clear()

    def decrement_vsplit(self):
        self.vsplit -= self.get_option('step_size')

    def increment_vsplit(self):
        self.vsplit += self.get_option('step_size')

    def decrease_master(self):
        self.decrement_vsplit()

        self.error_register_callback(self.increment_vsplit)
        self.enqueue()

    def increase_master(self):
        self.increment_vsplit()

        self.error_register_callback(self.decrement_vsplit)
        self.enqueue()
