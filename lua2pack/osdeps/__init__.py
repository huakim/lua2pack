import platform
def generate_args(parser):
    '''add generate command arguments'''
    parser.add_argument("--system", help="System name")
    parser.add_argument("--arch", help="Architecture name")
    parser.add_argument('--name', help="Override default name")

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
