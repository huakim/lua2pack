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


# Import the lua_type function from the lupa.lua module
from lupa.lua import lua_type
# Import the serialize function from the luadata module
from luadata import serialize as lua_ser
# Import the Mapping object
from collections.abc import Mapping


def is_enabled_flag_str(arg, not_arg, default):
    return lua_ser(is_enabled_flag(arg, not_arg, default))

# Define a function that declares a LuaMapping object for a given key
def DeclareLuaMapping(key):
    # Check if the key is a Lua table or a Mapping object
    if lua_type(key) == 'table':
        # If so, return a LuaMapping object for the key
        return LuaMapping(key)
    # Otherwise, return the key as is
    return key

# Define a LuaMapping class that inherits from the built-in dict class
def LuaMapping(_LuaMappingClass__lua_table):
    class LuaMappingClass(dict):
        # Initialize the LuaMapping object with the given argument
        def __init__(self):
            pass
        # Implement the __contains__ method
        def __contains__(self, key):
            return key in __lua_table.keys()
        # Implement the __getitem__ method to automatically declare LuaMapping objects for nested dictionaries
        def __getitem__(self, key):
            key = __lua_table[key]
            return DeclareLuaMapping(key)

        def __setitem__(self, key, value):
            __lua_table[key] = value

        def __delitem__(self, key):
            del __lua_table[key]

        def __contains__(self, key):
            return key in __lua_table

        def get(self, key, default=None):
            if key in self:
                return self[key]
            else:
                return default

        def pop(self, key, default=None):
            dd = self.get(key, default)
            del self[key]
            return dd

        def update(self, *args, **kwargs):
            j = {}
            j.update(*args, **kwargs)
            tb = __lua_table
            for i in j:
                tb[i] = j[i]

        def keys(self):
            j = list(__lua_table.keys())
            j.sort()
            return j

        def values(self):
            return map( lambda i: DeclareLuaMapping(self[i]),  self.keys() )

        def items(self):
            return map ( lambda i: [i, DeclareLuaMapping(self[i])],  self.keys() )

        def __iter__(self):
            return iter(self.keys())
        def __len__(self):
            return len(list(__lua_table.keys()))
        def __repr__(self):
            return lua_ser(self,indent=' ', indent_level=1)
        def __getattr__(self, name):
            return self[name]
        def __setattr__(self, name, value):
            self[name] = value
        def __delattr__(self, name):
            del self[name]
    return LuaMappingClass()

# Define a function that converts a Lua table to a string representation
def luadata_to_string(table):
    return repr(DeclareLuaMapping(table))
