class Container(object):
    CONTAINERS = {}
    idinc = 1

    def __init__(self, tiler, win):
        self.win = win
        self.tiler = tiler
        self.id = Container.idinc
        self.x, self.y, self.w, self.h = -1, -1, -1, -1

        self.win.set_container(self)

        Container.CONTAINERS[self.id] = self
        Container.idinc += 1

    def get_name(self):
        if not self.win:
            return 'Container #%d' % self.id

        return self.win.name

    def activate(self):
        self.win.activate()

    def switch(self, cont):
        self.win.container, cont.win.container = cont.win.container, self.win.container
        self.win, cont.win = cont.win, self.win

        self.fit_window()
        cont.fit_window()

    def moveresize(self, x, y, width, height):
        self.x, self.y, self.w, self.h = x, y, width, height
        self.fit_window()

    def fit_window(self):
        self.win.moveresize(self.x, self.y, self.w, self.h)

    def detach(self, reset_window=False):
        if reset_window:
            self.win.original_state()

        self.win.set_container(None)
        self.win = None

    def remove(self, reset_window=False):
        self.detach(reset_window)
        del Container.CONTAINERS[self.id]

    def __str__(self):
        ret = 'Container #%d' % self.id

        if self.win:
            ret += '\n\t' + str(self.win)
        else:
            ret += ' - Empty'

        return ret

    @staticmethod
    def lookup(cid):
        if cid in Container.CONTAINERS:
            return Container.CONTAINERS[cid]

        return None
