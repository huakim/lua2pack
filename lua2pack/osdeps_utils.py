from pkgutil import iter_modules

def list_submodules(module):
    for submodule in iter_modules(module.__path__):
        yield submodule.module_finder.find_module(submodule.name).load_module()

from . import osdeps
osdeps_submodules = [*list_submodules(osdeps), osdeps]

def generate_args(parser):
    '''add generate command arguments'''
    for i in osdeps_submodules:
        if hasattr(i, 'generate_args'):
            i.generate_args(parser)

def lua_code(args):
    '''add lua code'''
    return "\n".join([module.lua_code(args) for module in osdeps_submodules if hasattr(module, 'lua_code')])

