import ConfigParser
import os
import re

# This is PyTyle's custom configuration parser. There are two main
# goals accomplished with this sub-class:
#
# 1. It allows retrival of some other types, like lists, booleans, and
#    lists of certain types (namely, floats and ints).
# 2. It automatically parses Monitor/Workspace/Tiler specific configuration
#    sections and loads them into a tuple (wsid, mid, tiler) indexed
#    dictionary.
# 3. Iterfaces with the "option_types" dictionary specified below, allowing
#    for more automatic retrieval of configuration settings.
class PyTyleConfigParser(ConfigParser.SafeConfigParser):
    def getboolean(self, section, option):
        if self.get(section, option).lower() == 'yes':
            return True
        return False

    def getfloatlist(self, section, option):
        try:
            return map(
                float,
                self.getlist(section, option)
            )
        except ValueError:
            return self.getlist(section, option)

    def getintlist(self, section, option):
        try:
            return map(
                int,
                self.getlist(section, option)
            )
        except ValueError:
            return self.getlist(section, option)

    def getlist(self, section, option):
        def clean(s):
            return s.replace('"', '').replace("'", '')

        return map(
            clean,
            self.get(section, option).split()
        )

    def get_option(self, section, option):
        assert option in option_types

        return option_types[option]['exec'](self, section, option)

    def get_global_configs(self):
        retval = {}

        if 'Global' in self.sections():
            for option in self.options('Global'):
                retval[option] = self.get_option('Global', option)

        return retval

    def get_keybindings(self):
        retval = {}

        if 'Keybindings' in self.sections():
            for option in self.options('Keybindings'):
                retval[option] = self.get('Keybindings', option)

        return retval

    def get_wmt_configs(self):
        retval = {}

        all_tilers = self.get_option('Global', 'all_tilers')

        for section in self.sections():
            for tiler in all_tilers:
                m = re.match(
                    '^(Workspace([0-9]+)-?|Monitor([0-9]+)-?|' + tiler + '-?){1,3}$',
                    section
                )
                if m:
                    wsid = int(m.group(2)) if m.group(2) else None
                    mid = int(m.group(3)) if m.group(3) else None
                    tiler = tiler if tiler.lower() in section.lower() else None

                    retval[(wsid, mid, tiler)] = {}

                    for option in self.options(m.group(0)):
                        retval[(wsid, mid, tiler)][option] = self.get_option(
                            m.group(0),
                            option
                        )

        return retval

# A list of places to check for the configuration file
paths = [
    os.path.join('config.ini'),
    os.path.join('..', 'config.ini'),
    os.path.join('..', '..', 'config.ini')
]

# A list of supported options independent of section header.
# Please do not change settings here. The settings specified here
# are the minimal required for PyTyle to function properly.
option_types = {
    'all_tilers': {
        'exec': PyTyleConfigParser.getlist,
        'default': ['Vertical']
    },
    'movetime_offset': {
        'exec': PyTyleConfigParser.getfloat,
        'default': 0.5
    },
    'tilers': {
        'exec': PyTyleConfigParser.getlist,
        'default': ['Vertical']
    },
    'ignore': {
        'exec': PyTyleConfigParser.getlist,
        'default': []
    },
    'decorations': {
        'exec': PyTyleConfigParser.getboolean,
        'default': True
    },
    'margin': {
        'exec': PyTyleConfigParser.getintlist,
        'default': []
    },
    'tile_on_startup': {
        'exec': PyTyleConfigParser.getboolean,
        'default': False
    },
    'step_size': {
        'exec': PyTyleConfigParser.getfloat,
        'default': 0.05
    }
}

# Specified in the "Keybindings" section
keybindings = {}

# Settings specified in the "Global" section
glbls = {}

# A tuple (wsid, mid, tiler) indexed dictionary that allows for
# Monitor/Workspace/Tiler specific settings. The order or precedence
# (in descending order) is as follows:
#
#   Workspace/Monitor/Tiler
#   Workspace/Monitor
#   Workspace/Tiler
#   Monitor/Tiler
#   Workspace
#   Monitor
#   Tiler
#   Globals
#   Defaults (specified in option_types above)
#
# Options can be specified in section headers. The following are some
# valid examples:
#
# [Workspace0-Monitor1] or [Monitor1-Workspace0]
# Specifies options that only apply to the monitor indexed at 1 on
# the first workspace.
#
# [Horizontal]
# Specifies options that only apply to the Horizontal tiling layout.
#
# [Monitor0-Vertical] or [Vertical-Monitor0]
# Specifies options that only apply to the Vertical tiling layout on the
# monitor indexed at 0.
#
# [Monitor2-Horizontal-Workspace3] or any ordering thereof
# Specifies options that only apply to the Horizontal tiling layout on
# the monitor indexed at 2 and the fourth workspace.
#
# Essentially, any combination of "Workspace#", "Monitor#", or "[Tiling
# layout name]" is valid.
wmt = {}

# Loads the configuration file. This is called automatically when
# this module is imported, but it can also be called again when
# the settings ought to be refreshed.
def load_config_file():
    global glbls, keybindings, wmt, paths

    conf = PyTyleConfigParser()

    for path in paths:
        if os.path.isfile(path):
            conf.read(path)
            break

    glbls = conf.get_global_configs()
    keybindings = conf.get_keybindings()
    wmt = conf.get_wmt_configs()

# Just a public accessor to get a list of all the keybindings
def get_keybindings():
    global keybindings

    return keybindings

# A public accessor to obtain a value for an option. It takes
# precedence into account, therefore, this function should
# always be called with the most information available, unless
# otherwise desired.
def get_option(option, wsid=None, mid=None, tiler=None):
    global glbls, wmt, option_types

    # Cascade up... See the comments for the "wmt" variable
    # above for more details.

    # Generate lookup tuples... in order!
    attempts = [
        (wsid, mid, tiler),
        (wsid, mid, None),
        (wsid, None, tiler),
        (None, mid, tiler),
        (wsid, None, None),
        (None, mid, None),
        (None, None, tiler)
    ]

    for lookup in attempts:
        if lookup in wmt and option in wmt[lookup]:
            return wmt[lookup][option]

    if option in glbls:
        return glbls[option]
    else:
        return option_types[option]['default']

    return None

load_config_file()