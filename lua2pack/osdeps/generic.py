from . import is_enabled_flag_str as is_enabled_flag, store_flag

lua_code_extend_array = []


def lua_code_extend_flag_func(name, default):
    name = name.replace("-", "_")
    noname = "no_" + name

    def _(args):
        return name + " = " + is_enabled_flag(getattr(args, name), getattr(args, noname), default)

    lua_code_extend_array.append(_)

def generate_args(parser):
    for i, d in (
        ("subpackages", True),
        ("filelist", True),
        ("autobuildreqs", True),
        ("autoreqs", False),
        ("autoalternatives", False),
        ("skip-build-dependencies", False),
        ("skip-check-dependencies", False),
    ):
        store_flag(parser, i)
        lua_code_extend_flag_func(i, d)


def lua_code(args):
    return "\n".join(["""
prefix = package .. '-' .. version
archive = prefix .. '.tar.gz'
rockspec = prefix .. '.rockspec'
template = 'generic.spec'
"""] + [_(args) for _ in lua_code_extend_array])
