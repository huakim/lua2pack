from . import is_enabled_flag_str as is_enabled_flag, store_flag

def generate_args(parser):
    for i in ('subpackages', 'autogen', 'filelist', 'skip-build-dependencies', 'skip-check-dependencies'):
        store_flag(parser, i)

def lua_code(args):
    return f"""

prefix = package .. '-' .. version
archive = prefix .. '.tar.gz'
rockspec = prefix .. '.rockspec'

subpackages = {is_enabled_flag(args.subpackages, args.no_subpackages, True)}
autogen = {is_enabled_flag(args.autogen, args.no_autogen, False)}
filelist = {is_enabled_flag(args.filelist, args.no_filelist, True)}
skip_build_dependencies = {is_enabled_flag(args.skip_build_dependencies, args.no_skip_build_dependencies, False)}
skip_check_dependencies = {is_enabled_flag(args.skip_check_dependencies, args.no_skip_check_dependencies, False)}
template = 'generic.spec'

"""
