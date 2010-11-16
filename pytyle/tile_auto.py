from tile import Tile
from container import Container
from autostore import AutoStore

class AutoTile(Tile):
    def __init__(self, monitor):
        Tile.__init__(self, monitor)
        self.store = None
        self.cycle_index = 0

    def add(self, win):
        if (
            win.tilable() and self.tiling and
            win.get_winclass().lower() not in self.get_option('ignore')
        ):
            cont = Container(self, win)
            self.store.add(cont)
            self.enqueue()

    def borders_add(self, do_window=True):
        if self.store:
            for cont in self.store.all():
                cont.decorations(False, do_window)

    def borders_remove(self, do_window=True):
        if self.store:
            for cont in self.store.all():
                cont.decorations(True, do_window)

    def detach(self):
        self.tiling = False

        if self.store:
            for cont in self.store.all()[:]:
                cont.remove()

            self.store = None

    def remove(self, win, reset_window=False):
        if win.container and self.tiling:
            self.store.remove(win.container)
            win.container.remove(reset_window=reset_window)
            self.enqueue()

    # Helpers
    def _get_active(self):
        active = self.monitor.get_active()

        if active:
            if active.container and active.container in self.store.all():
                return active.container
            else:
                return self.store.all()[0]

        return None

    def _get_next(self):
        active = self._get_active()

        if active:
            a = self.store.all()
            m = self.store.masters
            s = self.store.slaves

            if active in m:
                if m.index(active) == 0:
                    return a[(a.index(m[-1]) + 1) % len(a)]
                else:
                    return a[(a.index(active) - 1) % len(a)]
            else:
                if s.index(active) == len(s) - 1:
                    return m[-1]
                else:
                    return a[(a.index(active) + 1) % len(a)]

        return None

    def _get_previous(self):
        active = self._get_active()

        if active:
            a = self.store.all()
            m = self.store.masters
            s = self.store.slaves

            if active in m:
                if m.index(active) == len(m) - 1:
                    return a[-1]
                else:
                    return a[(a.index(active) + 1) % len(a)]
            else:
                if s.index(active) == 0:
                    return m[0]
                else:
                    return a[(a.index(active) - 1) % len(a)]

        return None

    def _screen_focus(self, mid):
        new_tiler = self.workspace.get_monitor(mid).get_tiler()

        if self != new_tiler and new_tiler.tiling:
            active = new_tiler._get_active()

            if active:
                active.activate()
            elif new_tiler.store.masters:
                new_tiler.store.masters[0].activate()
            elif new_tiler.store.slaves:
                new_tiler.store.slaves[0].activate()
        elif self != new_tiler:
            active = self.workspace.get_monitor(mid).get_active()
            if active:
                active.activate()

    def _screen_put(self, mid):
        active = self._get_active()
        new_tiler = self.workspace.get_monitor(mid).get_tiler()

        if new_tiler != self and active and new_tiler.tiling:
            active.win.set_monitor(self.workspace.id, mid)
        elif active and self.monitor.id != mid and self.workspace.has_monitor(mid):
            mon = self.workspace.get_monitor(mid)
            active.win.moveresize(mon.wa_x, mon.wa_y, active.w, active.h)
            active.win.set_monitor(self.workspace.id, mid)

    # Commands
    def cycle(self):
        if self.store.masters and self.store.slaves:
            if self.cycle_index >= len(self.store.slaves):
                self.cycle_index = 0

            master = self.store.masters[0]
            slave = self.store.slaves[self.cycle_index]

            master.switch(slave)
            master.activate()

            self.cycle_index += 1

    def cycle_tiler(self):
        self.monitor.cycle()

    def decrease_master(self):
        pass

    def decrement_masters(self):
        self.store.dec_masters()
        self.enqueue()

    def float(self):
        active = self.monitor.get_active()

        if active and active.monitor.workspace.id == self.workspace.id and active.monitor.id == self.monitor.id:
            if not active.floating:
                active.floating = True
                self.remove(active, reset_window=True)
            else:
                active.floating = False
                self.add(active)

    def focus_master(self):
        master = self.store.masters[0]

        if master:
            master.activate()

    def increase_master(self):
        pass

    def increment_masters(self):
        self.store.inc_masters()
        self.enqueue()

    def make_active_master(self):
        if self.store.masters:
            active = self._get_active()
            master = self.store.masters[0]

            if active != master:
                master.switch(active)

    def next(self):
        next = self._get_next()

        if next:
            next.activate()

    def previous(self):
        previous = self._get_previous()

        if previous:
            previous.activate()

    def reset(self):
        self.monitor.tile_reset()

    def screen0_focus(self):
        self._screen_focus(0)

    def screen1_focus(self):
        self._screen_focus(1)

    def screen2_focus(self):
        self._screen_focus(2)

    def screen0_put(self):
        self._screen_put(0)

    def screen1_put(self):
        self._screen_put(1)

    def screen2_put(self):
        self._screen_put(2)

    def switch_next(self):
        active = self._get_active()
        next = self._get_next()

        if active and next:
            active.switch(next)

    def switch_previous(self):
        active = self._get_active()
        previous = self._get_previous()

        if active and previous:
            active.switch(previous)

    def tile(self):
        Tile.tile(self)

        if not self.store:
            self.store = AutoStore()

            active = self.monitor.get_active()

            if active:
                self.add(active)

            for win in self.monitor.iter_windows():
                if win != active:
                    self.add(win)

    def untile(self):
        Tile.untile(self)

        if self.store:
            for cont in self.store.all()[:]:
                cont.remove(reset_window=True)

            self.store = None

class AutoStore(object):
    def __init__(self):
        self.masters = []
        self.slaves = []
        self.mcnt = 1
        self.changes = False

    def made_changes(self):
        if self.changes:
            self.changes = False
            return True
        return False

    def add(self, cont, top = False):
        if len(self.masters) < self.mcnt:
            if cont in self.slaves:
                self.slaves.remove(cont)

            if top:
                self.masters.insert(0, cont)
            else:
                self.masters.append(cont)

            self.changes = True
        elif cont not in self.slaves:
            if top:
                self.slaves.insert(0, cont)
            else:
                self.slaves.append(cont)

            self.changes = True

    def remove(self, cont):
        if cont in self.masters:
            self.masters.remove(cont)

            if len(self.masters) < self.mcnt and self.slaves:
                self.masters.append(self.slaves.pop(0))

            self.changes = True
        elif cont in self.slaves:
            self.slaves.remove(cont)

            self.changes = True

    def switch(self, cont1, cont2):
        if cont1 in self.masters and cont2 in self.masters:
            i1, i2 = self.masters.index(cont1), self.masters.index(cont2)
            self.masters[i1], self.masters[i2] = self.masters[i2], self.masters[i1]
        elif cont1 in self.slaves and cont2 in self.slaves:
            i1, i2 = self.slaves.index(cont1), self.slaves.index(cont2)
            self.slaves[i1], self.slaves[i2] = self.slaves[i2], self.slaves[i1]
        elif cont1 in self.masters: # and cont2 in self.slaves
            i1, i2 = self.masters.index(cont1), self.slaves.index(cont2)
            self.masters[i1], self.slaves[i2] = self.slaves[i2], self.masters[i1]
        else: # cont1 in self.slaves and cont2 in self.masters
            i1, i2 = self.slaves.index(cont1), self.masters.index(cont2)
            self.slaves[i1], self.masters[i2] = self.masters[i2], self.slaves[i1]

    # Maybe I want to use the active window instead?
    def inc_masters(self):
        self.mcnt = min(self.mcnt + 1, len(self.all()))

        if len(self.masters) < self.mcnt and self.slaves:
            self.masters.append(self.slaves.pop(0))

    def dec_masters(self):
        if self.mcnt <= 0:
            return
        self.mcnt -= 1

        if len(self.masters) > self.mcnt:
            self.slaves.append(self.masters.pop())

    def all(self):
        return self.masters + self.slaves

    def __str__(self):
        r = 'Masters: %s\n' % [cont.get_name() for cont in self.masters]
        r += 'Slaves: %s\n' % [cont.get_name() for cont in self.slaves]

        return r
