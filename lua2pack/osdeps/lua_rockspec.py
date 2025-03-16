from . import luadata_to_string


# Define a function that returns a list of required OS dependencies
def requires_osdeps():
    return ["generic"]


# Define a function that generates Lua code to convert a Python object to a string
def lua_code(args):
    return (
        """
filename = package .. '-' .. version .. '.rockspec'
"""
        if args.template == "rock.rockspec"
        else ""
    )


def update_globals():
    return {"__data_to_string": luadata_to_string}
