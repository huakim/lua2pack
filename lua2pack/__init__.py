#!/usr/bin/python3
import platform
from .lua_runtime import LuaRuntime
import sys
import urllib.request
from pathlib import Path
import argparse
from .osdeps_utils import lua_code as os_specific_lua_code, generate_args as os_specific_generate_args
from os.path import isdir, isfile
from os import chdir
from .osdeps import LuaMapping
from os import path, listdir
import jinja2
import platformdirs

class Generator:
    def __init__(self, name, dir=path.dirname(path.abspath(__file__))):
        self.name = name
        self.dir = dir

    def default_file_template(self):
        return self.file_template_list()[0]

    @staticmethod
    def default_file_output(name, template):
        a = template.rsplit('.')
        if (len(a)) > 1:
            return name+'.'+a[1]
        else:
            return name

    def write_template(self, data, template, filename):
     #   if not filename:
     #       filename = "python-" + name + '.' + template.rsplit('.', 1)[1]   # take template file ending
        result = self.render(data, template)
        outfile = open(filename, 'wb')
        try:
            outfile.write(result)
        finally:
            outfile.close()

    def render(self, data, template):
   #     if not template:
   #         template = self.file_template_list()[0]
        env = self.prepare_template_env()
        template = env.get_template(template)
        return template.render(data).encode('utf-8')

    def get_template_dirs(self):

        """existing directories where to search for jinja2 templates. The order
    is important. The first found template from the first found dir wins!"""
        name=self.name
        return filter(lambda x: path.exists(x), [
            path.join(i, "templates") for i in (
        # user dir
            path.join(path.expanduser('~'), f".{name}"),
            platformdirs.user_data_dir(appname=name),
            platformdirs.user_config_dir(appname=name),
        # usually inside the site-packages dir
            self.dir,
        # system wide dir
            *platformdirs.site_data_dir(appname=name, multipath=True).split(":"),
        )])

    def prepare_template_env(self):
    # setup jinja2 environment with custom filters
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.get_template_dirs()))
        env.filters['parenthesize_version'] = \
            lambda s: re.sub('([=<>]+)(.+)', r' (\1 \2)', s)
        env.filters['basename'] = \
            lambda s: s[s.rfind('/') + 1:]
        return env

    def file_template_list(self):
        template_files = []
        for d in self.get_template_dirs():
            template_files += [f for f in listdir(d) if not f.startswith('.')]
        return template_files

def read_rockspec(path_or_uri):
    from glob import glob
    content = None
    stw = path_or_uri.startswith
    if path_or_uri == "<stdin>":
        # Read from stdin
        return sys.stdin.read()
    elif stw('glob:'):
        path_or_uri = path_or_uri[5:]
        # Get files from glob
        files = [i for i in glob(path_or_uri, recursive=True) if isfile(i)]
        # If files not found
        if not files:
            raise FileNotFoundError("Error: didn't found files by glob {}".format(path_or_uri))
    elif stw("text:"):
        # Return text
        return path_or_uri[5:]
    elif stw("http://") or stw("https://"):
        # Read from a URI
        try:
            return urllib.request.urlopen(path_or_uri).read().decode('utf-8')
        except urllib.error.HTTPError as e:
            raise Exception("Error reading rockspec from URI: {} (HTTP {})".format(path_or_uri, e.code))
    else:
        files = [path_or_uri]
    content = ''
    for path_or_uri in files:
        with open(path_or_uri, 'r') as file:
            content += file.read() + "\n"
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
duplicates = (lambda array: ['add_'+i for i in array] + ['add_luarock_'+i for i in array]) ((*map(lambda a: a+"_requires", ('build', 'check', 'preun', 'pre', 'postun', 'post', 'pretrans', 'posttrans')), 'requires', 'provides', 'recommends'))

def main(args=None):
    # Create the parser
    mainparser = argparse.ArgumentParser(description="A Python script that generates a rockspec file")
    # set defaults
    mainparser.set_defaults(func=lambda *a: mainparser.print_help())
    # add subparsers
    subparsers = mainparser.add_subparsers(title='commands')
    # add generate command
    parser = subparsers.add_parser('generate', help="generate RPM spec or DEB dsc file for a rockspec specification")
    # Define generator's template environment
    generator = generate_rockspec('lua2pack', __path__[0])
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
    # Execute function
    args.func(args)

if __name__ == "__main__":
    main()

