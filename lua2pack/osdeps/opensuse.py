from .. import is_enabled_array

def generate_args(parser):
    parser.add_argument('--subpackages', action='store', nargs='*')
    parser.add_argument('--autogen', action='store', nargs='*')
    parser.add_argument('--filelist', action='store', nargs='*')
    parser.add_argument('--skip-build-dependencies', action='store', nargs='*')
    parser.add_argument('--skip-check-dependencies', action='store', nargs='*')
    parser.add_argument('--no-subpackages', action='store', nargs='*')
    parser.add_argument('--no-autogen', action='store', nargs='*')
    parser.add_argument('--no-filelist', action='store', nargs='*')
    parser.add_argument('--no-skip-build-dependencies', action='store', nargs='*')
    parser.add_argument('--no-skip-check-dependencies', action='store', nargs='*')


def lua_code(args):
    return f"""

subpackages = {is_enabled_array(args.subpackages, args.no_subpackages, True)}
autogen = {is_enabled_array(args.autogen, args.no_autogen, False)}
filelist = {is_enabled_array(args.filelist, args.no_filelist, True)}
skip_build_dependencies = {is_enabled_array(args.skip_build_dependencies, args.no_skip_build_dependencies, False)}
skip_check_dependencies = {is_enabled_array(args.skip_check_dependencies, args.no_skip_check_dependencies, False)}
template = 'generic.spec'

"""
