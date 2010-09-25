from container import Container
from window import Window

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

    def inc_masters(self):
        self.mcnt += 1

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
