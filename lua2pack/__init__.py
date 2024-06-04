#!/usr/bin/python3
import platform
import lupa
import sys
import urllib.request
import argparse
from jinja2_easy.generator import Generator
from .osdeps_utils import lua_code as os_specific_lua_code, generate_args as os_specific_generate_args

def read_rockspec(path_or_uri):
    content = None

    if path_or_uri == "<stdin>":
        # Read from stdin
        content = sys.stdin.read()
    elif path_or_uri == "<none>":
        # Return empty string
        return ''
    elif path_or_uri.startswith("http://") or path_or_uri.startswith("https://"):
        # Read from a URI
        try:
            response = urllib.request.urlopen(path_or_uri)
            content = response.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            raise Exception("Error reading rockspec from URI: {} (HTTP {})".format(path_or_uri, e.code))
    else:
        # Read from a local file
        try:
            with open(path_or_uri, 'r') as file:
                content = file.read()
        except FileNotFoundError:
            raise Exception("Error reading rockspec file: {}".format(path_or_uri))

    return content

class generate_rockspec(Generator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    # function used for generating rockspec specification
    def rockspec(generator, args):

        # get rockspec path
        rockspec_path = args.rockspec
        luacode = args.luacode or []
        defines = args.define or []
        cache={}
        newline="\n"
        # generate lua code (luarocks rockspec contains an lua compatible code)
        luaprog = f'''
{read_rockspec(rockspec_path)}
{os_specific_lua_code(args)}
{newline.join([cache[a]  for a in duplicates if custom_dependency(args, a, cache)] + luacode + [a[0] + '=' + a[1] for a in defines if len(a) >  1])}
'''
        # create lua runtime
        lua = lupa.LuaRuntime()
        # execute code
        lua.execute(luaprog)
        # get lua globals
        return lua.globals()
    # function used for generating from template
    def __call__(generator, args):
        rockspec = generator.rockspec(args)
        template = args.template or rockspec.template
        filename = args.filename or generator.default_file_output(rockspec.name, template)
        generator.write_template(rockspec, template, filename)


def custom_dependency(args, name, cache):
    try:
        array = getattr(args, name)
        if array is None:
            return False
    except AttributeError:
        return False
    if not name in cache:
        cache[name] = name+'={'+','.join(map(repr, array))+'}'
    return True

# Create requirement duplicates
duplicates = (lambda array: ['add_'+i for i in array] + ['add_luarock_'+i for i in array]) ((*map(lambda a: a+"_requires", ('build', 'check', 'preun', 'pre', 'postun', 'post', 'pretrans', 'posttrans')), 'requires', 'provides', 'recommends'))

def main(args=None):
    # Create the parser
    mainparser = argparse.ArgumentParser(description="A Python script that generates a rockspec file")
    # add subparsers
    subparsers = mainparser.add_subparsers(title='commands')
    # add generate command
    parser = subparsers.add_parser('generate', help="generate RPM spec or DEB dsc file for a rockspec specification")
    # Define generator's template environment
    generator = generate_rockspec('lua2pack', __path__[0])
    # Define the command-line arguments
    # Rockspec file
    parser.add_argument("--rockspec", help="Path to the rockspec file or URI", default='<none>')
    # Define lua parameters
    parser.add_argument("--define", help="Override some lua parameters", type=str, action='append', nargs='*')
    # Add specific lua code
    parser.add_argument("--luacode", help="Override some lua codes", type=str, action='append')
    # Add duplicates
    for i in duplicates:
        parser.add_argument('--'+i.replace('_', '-'), help=f"Additional {i.replace('_', ' ')} dependencies to be added", type=str, action='append')

    os_specific_generate_args(parser)

    # Template file for generate command
    parser.add_argument('-t', '--template', choices=generator.file_template_list(), help='file template')
    # Template output filename for generate command
    parser.add_argument('-f', '--filename', help='spec filename (optional)')
    # Function for generate command
    parser.set_defaults(func=generator)
    # Parse arguments
    args = mainparser.parse_args(args)
    # Execute function
    args.func(args)

if __name__ == "__main__":
    main()

