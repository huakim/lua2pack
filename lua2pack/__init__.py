#!/usr/bin/python3
import platform
from .lua_runtime import LuaRuntime
import sys
from pathlib import Path
import argparse
from .osdeps_utils import lua_code as os_specific_lua_code, generate_args as os_specific_generate_args, mount_adapter
from os.path import isdir, isfile
from os import chdir
from .osdeps import DeclareLuaMapping as LuaMapping
from os import path, listdir
from jinja2_easy.generator import Generator
import platformdirs

from requests import Session
from requests.exceptions import RequestException
from requests_glob import FileAdapter
from requests_text import TextAdapter
from requests_stdin import StdinAdapter

def read_rockspec(path_or_url):
    s = Session()
    s.mount('file://', FileAdapter())
    s.mount('text://', TextAdapter())
    s.mount('stdin://',StdinAdapter())
    mount_adapter(s)
    try:
        return s.get(path_or_url).text
    except RequestException:
        return open(path_or_url, 'r').read()

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
{newline.join(read_rockspec(rockspec_path_i) for rockspec_path_i in rockspec_path)}
{os_specific_lua_code(args)}
{newline.join([cache[a]  for a in duplicates if custom_dependency(args, a, cache)] + luacode + [a[0] + '=' + a[1] for a in defines if len(a) >  1])}
'''
        # create lua runtime
        lua = LuaRuntime()
        # execute code
        lua.execute(luaprog)
        # get lua globals
        return lua.globals()
    # function used for generating from template
    def __call__(generator, args):
        rockspec = generator.rockspec(args)
        template = args.template or rockspec.template
        filename = args.filename or rockspec.filename or generator.default_file_output(rockspec.name, template)
        outdir = args.outdir or rockspec.outdir
        if outdir and isdir(outdir):
            chdir(outdir)
        generator.write_template(LuaMapping(rockspec), template, filename)


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
duplicates = (lambda array: ['add_'+i for i in array] + ['add_luarocks_'+i for i in array]) ((*map(lambda a: a+"_requires", ('build', 'check', 'preun', 'pre', 'postun', 'post', 'pretrans', 'posttrans')), 'requires', 'provides', 'recommends'))

# Define generator's template environment
generator = generate_rockspec('lua2pack', __path__[0])

def main(args=None):
    # Create the parser
    mainparser = argparse.ArgumentParser(description="A Python script that generates a rockspec file")
    # set defaults
    mainparser.set_defaults(func=lambda *a: mainparser.print_help())
    # add noop operation
    mainparser.add_argument("--noop", help='', type=str, default='disable')
    # add subparsers
    subparsers = mainparser.add_subparsers(title='commands')
    # add generate command
    parser = subparsers.add_parser('generate', help="generate RPM spec or DEB dsc file for a rockspec specification")
    # add noop operation
    parser.add_argument("--noop", help='', type=str, default='disable')
    # Define the command-line arguments
    # Rockspec file
    parser.add_argument("--rockspec", help="Path to the rockspec file or URI", type=str, action='append')
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
    parser.add_argument('-f', '--filename', help='output filename (optional)')
    # Template output directory for generate command
    parser.add_argument('--outdir', help='out directory (used by obs service)')
    # Function for generate command
    parser.set_defaults(func=generator)
    # Parse arguments
    args = mainparser.parse_args(args)
    # Check if noop is enabled, if yes, then exit
    if args.noop.lower() in ['enable', 'yes', 'true', 'y']:
       return
    # Execute function
    args.func(args)

if __name__ == "__main__":
    main()

