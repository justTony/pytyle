import ConfigParser, os

class PyTyleConfigParser(ConfigParser.SafeConfigParser):
    def getlist(self, section, option):
        def clean(s):
            return s.replace('"', '').replace("'", '')

        return map(
            clean,
            self.get(section, option).split()
        )


conf = PyTyleConfigParser()
conf.read(os.path.join('/', 'home', 'andrew', 'PyTyle2', 'src', 'config.ini'))

tilers = conf.getlist('Options', 'tilers')
movetime_offset = conf.getfloat('Options', 'movetime_offset')
ignore = conf.getlist('Options', 'ignore')

keybindings = {
    option: conf.get('Keybindings', option)
    for option in conf.options('Keybindings')
}
