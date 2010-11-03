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

        if m_height <= 0 or m_height > self.monitor.wa_height or s_height <= 0 or s_height > self.monitor.wa_height:
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

    def increase_master(self, inc = 0.05):
        self.vsplit += inc
        self.enqueue()

    def decrease_master(self, dec = 0.05):
        self.vsplit -= dec
        self.enqueue()
