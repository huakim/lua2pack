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
from toposort import toposort_flatten

class SortedOsdepsSubmodules:
    def __init__(self, module, package, dictionary, module_list):
        self.__pkgname__ = package.__name__
        self.__module_list__ = module_list
        self.__iterable__ = None
        self.__dictionary__ = dictionary

    def __iter__(self):
        iterable = self.__iterable__
        if iterable is None:
            pkgname = self.__pkgname__
            dictionary = self.__dictionary__
            module_list = self.__module_list__
            iterable = { dictionary[f'{pkgname}.{str(module_name)}'] for module_name in module_list }
            self.__iterable__ = iterable
        return iterable.__iter__()


class SortedOsdepsModules:
    def __init__(self, items, main_package, func_name='requires_osdeps'):
        self.__list_items = {item.__name__ : item for item in items}
        self.__func_name = func_name
        self.__unsorted = main_package

    def __getrequires__(self, mod):
        func_name = self.__func_name
        if hasattr(mod, func_name):
            return SortedOsdepsSubmodules(mod, self.__unsorted, self.__list_items, getattr(mod, func_name)())
        return []

    def __iter__(self):
        items = self.__list_items
        unsorted = self.__unsorted
        if not unsorted is None:
            items = toposort_flatten( { i: self.__getrequires__(i) for i in items.values() }, False )
            self.__unsorted = None
            self.__list_items = items
        return items.__iter__()

osdeps_submodules = list(SortedOsdepsModules(import_submodules(osdeps), osdeps, 'requires_osdeps'))

osdeps_update_globals = [i.update_globals for i in [osdeps, *osdeps_submodules] if hasattr(i, 'update_globals')]

osdeps_generate_args = [ i.generate_args for i in [osdeps, *SortedOsdepsModules(osdeps_submodules, osdeps, 'requires_generate_args')] if hasattr(i, 'generate_args')]

osdeps_lua_code = [ i.lua_code for i in [osdeps, *SortedOsdepsModules(osdeps_submodules, osdeps, 'requires_lua_code')] if hasattr(i, 'lua_code')]

def update_globals(global_dict):
    '''update globals'''
    for func in osdeps_update_globals:
        global_dict.update(func())

def generate_args(parser):
    '''add generate command arguments'''
    for func in osdeps_generate_args:
        func(parser)

def lua_code(args):
    '''add lua code'''
    return "\n".join([lua_code(args) for lua_code in osdeps_lua_code])

