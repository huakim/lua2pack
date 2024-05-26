#!/usr/bin/python3
import platform
import lupa
import sys
import urllib.request
import argparse
from jinja2_easy.generator import Generator
from os import getcwd
from .osdeps import os_specific_code, os_specific_args

def read_rockspec(path_or_uri):
    content = None

    if path_or_uri == "<stdin>":
        # Read from stdin
        content = sys.stdin.read()
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

def custom_dependency(args, name, cache):
    try:
        array = getattr(args, name)
        if array is None:
            return False
    except AttributeError:
        return False
    joint = ','.join(map(repr, array))
    cache[name] = name + '={' + joint + '}'
    return True

def duplicate(*array):
    return ['add_'+i for i in array] + ['add_luarock_'+i for i in array]

def main(args=None):
# Create the parser
    parser = argparse.ArgumentParser(description="A Python script that generates a rockspec file")
    generator = Generator('lua2rpm', getcwd())
# Define the command-line arguments

    parser.add_argument("--rockspec", help="Path to the rockspec file or URI", default='<stdin>')

    parser.add_argument("--define", help="Override some lua parameters", type=str, action='append', nargs='*')

    parser.add_argument("--luacode", help="Override some lua codes", type=str, action='append')

    duplicates = duplicate(*map(lambda a: a+"_requires", ('build', 'check', 'preun', 'pre', 'postun', 'post', 'pretrans', 'posttrans')), 'requires', 'provides', 'recommends')

    for i in duplicates:
        parser.add_argument('--'+i.replace('_', '-'), help=f"Additional {i.replace('_', ' ')} dependencies to be added", type=str, action='append')

    parser.add_argument('-t', '--template', choices=generator.file_template_list(), default='generic.spec', help='file template')
    os_specific_args(parser)
    parser.add_argument('-f', '--filename', help='spec filename (optional)')
# Parse the command-line arguments
    args = parser.parse_args(args)

    rockspec_path = args.rockspec
    luacode = args.luacode or []
    defines = args.define or []
    cache={}
    newline="\n"
    luaprog = f'''
{read_rockspec(rockspec_path)}
{os_specific_code(args)}
{newline.join([cache[a]  for a in duplicates if custom_dependency(args, a, cache)] + luacode + [a[0] + '=' + a[1] for a in defines if len(a) >  1])}
'''
    lua = lupa.LuaRuntime()
    lua.execute(luaprog)
    rockspec = lua.globals()
    template = args.template
    filename = args.filename or generator.default_file_output('lua-'+rockspec.name, template)
    generator.write_template(rockspec, template, filename)

    return rockspec

if __name__ == "__main__":
    main()

