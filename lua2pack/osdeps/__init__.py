import platform
from requests_glob import GlobAdapter

def generate_args(parser):
    '''add generate command arguments'''
    parser.add_argument("--system", help="System name")
    parser.add_argument("--arch", help="Architecture name")
    parser.add_argument('--name', help="Override default name")

def store_flag(parser, name):
    parser.add_argument('--'+name, action='store', nargs='*')
    parser.add_argument('--no-'+name, action='store', nargs='*')

def is_enabled_array(array, default=False, revert=False):
    if not array is None:
        default = array[0] == 'enable' if len(array) > 0 else True
        if revert:
            default = not default
    return not not default

def is_enabled_flag(arg, not_arg, default):
    return is_enabled_array(arg if default else not_arg,
        is_enabled_array(not_arg if default else arg,
            default, default), not default)


def mount_adapter(adapter):
    adapter.mount('glob://', GlobAdapter())

def lua_code(args):
    '''add lua code'''
    system = args.system or platform.system()
    machine = args.arch or platform.machine()
    name = args.name
    name = repr(name) if name else "'lua-'..package"

    return f"""

major, minor = string.match(version, "(.-)%-(.*)")
system = {repr(system)}
arch = {repr(machine)}

name = {name}

"""

# Import the serialize function from the luadata module
from luadata import serialize as lua_ser
# Import the Mapping object
from collections.abc import Mapping


def is_enabled_flag_str(arg, not_arg, default):
    return lua_ser(is_enabled_flag(arg, not_arg, default))

from luadata.luatable import LuaTable as DeclareLuaMapping

# Define a function that converts a Lua table to a string representation
def luadata_to_string(table):
    return repr(DeclareLuaMapping(table))
