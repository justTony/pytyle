import config
from command import Command
from container import Container

class Tile(object):
    queue_tile = set()

    @staticmethod
    def dispatch(monitor, command):
        assert isinstance(command, Command)

        tiler = monitor.get_tiler()

        if tiler:
            if tiler.get_name() == 'ManualTile':
                cmd_nm = command.get_manual_command()
            else:
                cmd_nm = command.get_auto_command()

            if hasattr(tiler, cmd_nm):
                if command == 'tile':
                    tiler.enqueue(force_tiling=True)
                elif tiler.tiling:
                    getattr(tiler, cmd_nm)()
            else:
                raise Exception('Invalid command %s' % cmd_nm)

    @staticmethod
    def exec_queue():
        for tiler in Tile.queue_tile:
            tiler.tile()
        Tile.queue_tile = set()

    def __init__(self, monitor):
        self.workspace = monitor.workspace
        self.monitor = monitor
        self.tiling = False
        self.decor = self.get_option('decorations')
        self.borders = self.get_option('borders')
        self.queue_error = set()

    def borders_add(self, do_window=True):
        pass

    def borders_remove(self, do_window=True):
        pass

    def callback_hidden(self):
        if not self.decor:
            self.borders_remove(do_window=False)

    def callback_visible(self):
        if not self.decor:
            self.borders_add(do_window=False)

    def enqueue(self, force_tiling=False):
        if self.tiling or force_tiling:
            Tile.queue_tile.add(self)

    def error_clear(self):
        self.queue_error = set()

    def error_exec_callbacks(self):
        for err in self.queue_error:
            err()
        self.error_clear()

    def error_register_callback(self, exc):
        self.queue_error.add(exc)

    def get_name(self):
        return self.__class__.__name__

    def get_option(self, option):
        return config.get_option(
            option,
            self.workspace.id,
            self.monitor.id,
            self.get_name()
        )

    # Commands
    def tile(self):
        self.tiling = True
        self.monitor.tiler = self

    def toggle_borders(self):
        self.borders = not self.borders

        if not self.decor:
            if self.borders:
                self.borders_add(do_window=False)
            else:
                self.borders_remove(do_window=False)

    def toggle_decorations(self):
        self.decor = not self.decor

        if self.decor:
            self.borders_remove()
        else:
            self.borders_add()

        Container.manage_focus(self.monitor.get_active())

    def untile(self):
        self.tiling = False
        self.monitor.tiler = None
