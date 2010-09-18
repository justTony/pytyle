from pytyle.tile import AutoTile
from pytyle.autostore import AutoStore
from pytyle.window import Window

class Vertical(AutoTile):
    def __init__(self, wsid, mid):
        AutoTile.__init__(self, wsid, mid)

    def tile(self):
        AutoTile.tile(self)

        print self.store

        m_size = len(self.store.masters)
        s_size = len(self.store.slaves)

        m_width = self.monitor.wa_width / 2
        s_width = self.monitor.wa_width - m_width

        m_x = self.monitor.wa_x
        s_x = m_x + m_width

        if m_size:
            m_height = self.monitor.wa_height / m_size

            if not s_size:
                m_width = self.monitor.wa_width

            for i, wid in enumerate(self.store.masters):
                print m_x, i * m_height, m_width, m_height
                Window.lookup(wid).moveresize(
                    m_x,
                    i * m_height,
                    m_width,
                    m_height
                )

        if s_size:
            s_height = self.monitor.wa_height / s_size

            if not m_size:
                s_width = self.monitor.wa_width

            for i, wid in enumerate(self.store.slaves):
                # print s_x, i * s_height, s_width, s_height
                Window.lookup(wid).moveresize(
                    s_x,
                    i * s_height,
                    s_width,
                    s_height
                )
