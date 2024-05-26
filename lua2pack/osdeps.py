def os_specific_args(parser):
    parser.add_argument("--system", help="System name")
    parser.add_argument("--arch", help="Architecture name")
    parser.add_argument('--name', help="Override default name")

def os_specific_code(args):
    system = args.system or platform.system()
    machine = args.arch or platform.machine()
    name = args.name
    name = repr(name) if name else 'package'

    return f"""

prefix = package .. '-' .. version
source = prefix .. '.tar.gz'
rockspec = prefix .. '.rockspec'
major, minor = string.match(version, "(.-)%-(.*)")
system = {repr(system)}
arch = {repr(machine)}

name = {name}

subpackages = true
autogen = false
filelist = true
skip_build_dependencies = false
skip_check_dependencies = false

"""

