def import_submodules(module, recursive=False):
    """Import all submodules of a module, recursively."""
    from sys import modules
    from pkgutil import walk_packages
    from importlib.util import module_from_spec
    module_stack = [walk_packages(
        module.__path__,
        module.__name__ + '.')
    ]
    while module_stack:
        gen = module_stack.pop()
        for loader, module_name, is_pkg in gen:
            _spec = loader.find_spec(module_name)
            _module = module_from_spec(_spec)
            _spec.loader.exec_module(_module)
            modules[module_name] = _module
            yield _module
            if recursive:
                module_stack.append(
                     walk_packages(
                         _module.__path__,
                         _module.__name__ + '.'
                     )
                )

from . import osdeps
osdeps_submodules = [*import_submodules(osdeps), osdeps]

def generate_args(parser):
    '''add generate command arguments'''
    for i in osdeps_submodules:
        if hasattr(i, 'generate_args'):
            i.generate_args(parser)

def lua_code(args):
    '''add lua code'''
    return "\n".join([module.lua_code(args) for module in osdeps_submodules if hasattr(module, 'lua_code')])

