from window import Window

class AutoStore(object):
    def __init__(self):
        self.masters = []
        self.slaves = []
        self.mcnt = 1

    def add(self, wid, top = False):
        if len(self.masters) < self.mcnt:
            if wid in self.slaves:
                self.slaves.remove(wid)

            if top:
                self.masters.insert(0, wid)
            else:
                self.masters.append(wid)
        else:
            if top:
                self.slaves.insert(0, wid)
            else:
                self.slaves.append(wid)

    def remove(self, wid):
        if wid in self.masters:
            self.masters.remove(wid)

            if len(self.masters) < self.mcnt:
                self.masters.append(self.slaves.pop(0))
        elif wid in self.slaves:
            self.slaves.remove(wid)

    def switch(self, wid1, wid2):
        if wid1 in self.masters and wid2 in self.masters:
            i1, i2 = self.masters.index(wid1), self.masters.index(wid2)
            self.masters[i1], self.masters[i2] = self.masters[i2], self.masters[i1]
        elif wid1 in self.slaves and wid2 in self.slaves:
            i1, i2 = self.slaves.index(wid1), self.slaves.index(wid2)
            self.slaves[i1], self.slaves[i2] = self.slaves[i2], self.slaves[i1]
        elif wid1 in self.masters: # and wid2 in self.slaves
            i1, i2 = self.masters.index(wid1), self.slaves.index(wid2)
            self.masters[i1], self.slaves[i2] = self.slaves[i2], self.masters[i1]
        else: # wid1 in self.slaves and wid2 in self.masters
            i1, i2 = self.slaves.index(wid1), self.masters.index(wid2)
            self.slaves[i1], self.masters[i2] = self.masters[i2], self.slaves[i1]

    def inc_masters(self):
        self.mcnt += 1

    def dec_masters(self):
        if self.mcnt <= 0:
            return
        self.mcnt -= 1

    def all(self):
        return self.masters + self.slaves

    def __str__(self):
        r = 'Masters: %s\n' % [Window.lookup(wid).name for wid in self.masters]
        r += 'Slaves: %s\n' % [Window.lookup(wid).name for wid in self.slaves]

        return r
