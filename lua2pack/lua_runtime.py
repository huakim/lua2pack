import lupa
from .osdeps_utils import update_globals


class LuaRuntime:
    def __init__(self):
        self.__lua = lupa.LuaRuntime()
        update_globals(self)

    def __getattr__(self, name):
        return getattr(self.__lua, name)

    def update(self, dct):
        gb = self.globals()
        for i in dct:
            gb[i] = dct[i]
