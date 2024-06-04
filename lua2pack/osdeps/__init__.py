import platform
def generate_args(parser):
    '''add generate command arguments'''
    parser.add_argument("--system", help="System name")
    parser.add_argument("--arch", help="Architecture name")
    parser.add_argument('--name', help="Override default name")

class LuaBool():
    def __init__(self, a):
        self.__a = bool(a)
    def __bool__(self):
        return self.__a
    def __str__(self):
        return 'true' if self else 'false'

def is_enabled_array(array, default=False, revert=False):
    if not array is None:
        default = array[1] == 'enable' if len(array) > 0 else True
        if revert:
            default = not default
    return LuaBool(default)

def is_enabled_flag(arg, not_arg, default):
    return is_enabled_array(not_arg if default else arg,
        is_enabled_array(arg if default else not_arg,
            default, default), not default)

def lua_code(args):
    '''add lua code'''
    system = args.system or platform.system()
    machine = args.arch or platform.machine()
    name = args.name
    name = repr(name) if name else "'lua-'..package"

    return f"""

prefix = package .. '-' .. version
source = prefix .. '.tar.gz'
rockspec = prefix .. '.rockspec'
major, minor = string.match(version, "(.-)%-(.*)")
system = {repr(system)}
arch = {repr(machine)}

name = {name}

"""
