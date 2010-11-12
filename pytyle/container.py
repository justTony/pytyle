import ptxcb

class Container(object):
    idinc = 1
    active = None

    @staticmethod
    def manage_focus(win):
        if win and win.container:
            win.container.borders_activate(win.container.tiler.decor)
        elif Container.active:
            Container.active.borders_normal(Container.active.tiler.decor)

    def __init__(self, tiler, win):
        self.win = win
        self.tiler = tiler
        self.id = Container.idinc
        self.x, self.y, self.w, self.h = -1, -1, -1, -1

        self.win.set_container(self)

        Container.idinc += 1

        self._box = {
            'htop': None, 'hbot': None,
            'vleft': None, 'vright': None
        }

    def activate(self):
        if self.win:
            self.win.activate()

    def borders_activate(self, decor):
        if Container.active and Container.active != self:
            Container.active.borders_normal(Container.active.tiler.decor)

        Container.active = self

        if not decor:
            self.box_show(0xff0000)

    def borders_normal(self, decor):
        if not decor:
            self.box_show(0x008800)

    def box_hide(self):
        for box in self._box.values():
            if box:
                box.close()

    def box_show(self, color=0x000000):
        x, y, w, h = self.x, self.y, self.w, self.h

        bw = 2

        self.box_hide()

        if self.tiler.workspace.id == ptxcb.XROOT.get_current_desktop():
            self._box['htop'] = ptxcb.LineWindow(self.tiler.workspace.id, x, y, w, bw, color)
            self._box['hbot'] = ptxcb.LineWindow(self.tiler.workspace.id, x, y + h, w, bw, color)
            self._box['vleft'] = ptxcb.LineWindow(self.tiler.workspace.id, x, y, bw, h, color)
            self._box['vright'] = ptxcb.LineWindow(self.tiler.workspace.id, x + w - bw, y, bw, h, color)

    def decorations(self, decor, do_window=True):
        if do_window and self.win:
            self.win.decorations(decor)

        if not decor:
            if self == Container.active or (self.win and self.win.id == ptxcb.XROOT.get_active_window()):
                self.borders_activate(decor)
            else:
                self.borders_normal(decor)
        else:
            self.box_hide()

    def detach(self, reset_window=False):
        if reset_window:
            self.win.original_state()

        self.win.set_container(None)
        self.win.decorations(True)
        self.win = None

    def fit_window(self):
        # Don't do anything if the pointer is on the window...
        if not self.win or self.win.moving:
            return

        if (self.x != -1 and self.y != -1
            and self.w != -1 and self.h != -1):
            self.win.moveresize(self.x, self.y, self.w, self.h)

    def get_name(self):
        if not self.win:
            return 'Container #%d' % self.id

        return self.win.name

    def moveresize(self, x, y, width, height):
        self.x, self.y, self.w, self.h = x, y, width, height
        self.fit_window()

        self.decorations(self.tiler.decor)

    def remove(self, reset_window=False):
        self.detach(reset_window)

        self.box_hide()

        if self == Container.active:
            Container.active = None

    def switch(self, cont):
        self.win.container, cont.win.container = cont.win.container, self.win.container
        self.win, cont.win = cont.win, self.win

        if Container.active == cont:
            self.borders_activate(self.tiler.decor)
        elif Container.active == self:
            cont.borders_activate(cont.tiler.decor)

        self.fit_window()
        cont.fit_window()

    def __str__(self):
        ret = 'Container #%d' % self.id

        if self.win:
            ret += '\n\t' + str(self.win)
        else:
            ret += ' - Empty'

        return ret
