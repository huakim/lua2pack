#!/usr/bin/python3
import sys

for i in [
    "jinja2_easy.generator",
    "luadata.luatable",
    "requests_file",
    "requests_glob",
    "requests_stdin",
    "requests_text",
]:
    submodule = __name__ + ".bundled." + i.split(".")[0] + "." + i
    try:
        sys.modules[i] = __import__(submodule)
    except ImportError:
        pass


from .lua_runtime import LuaRuntime
import argparse
from .osdeps_utils import (
    lua_code as os_specific_lua_code,
    generate_args as os_specific_generate_args,
    mount_adapter,
)
from os.path import join, isdir
from os import chdir, listdir, getcwd
from .osdeps import DeclareLuaMapping as LuaMapping, is_enabled, store_flag

from .bundled.jinja2_easy.jinja2_easy.generator import Generator

import subprocess
import tempfile
import sys
import tarfile

from requests import Session
from requests.exceptions import RequestException
from .bundled.requests_glob.requests_glob import FileAdapter
from .bundled.requests_text.requests_text import TextAdapter
from .bundled.requests_stdin.requests_stdin import StdinAdapter


class GetCwd:
    def __repr__(self):
        return getcwd()


def fetch(args):
    # Step 1: Create a temporary directory
    outdir = args.outdir
    with tempfile.TemporaryDirectory() as temp_dir:
        # set output directory
        tmp = args.outdir = str(temp_dir)

        if is_enabled(args, "tostdout"):
            resultdir = tmp
        elif not outdir:
            resultdir = getcwd()
        else:
            resultdir = outdir
        # set template to rock.rockspec
        args.template = "rock.rockspec"
        # Generate rockspec file in temporary directory
        generator(args)
        # Find the generated rockspec file
        rockspec_files = [f for f in listdir(temp_dir) if f.endswith(".rockspec")]
        if not rockspec_files:
            raise Exception("No .rockspec files found in the temporary directory.")
            return
        rockspec_file = join(tmp, rockspec_files[0])
        # Run luarocks pack in the temporary directory
        if (subprocess.run(["luarocks", "pack", rockspec_file], cwd=temp_dir, check=True).returncode == 0):
            print(f"Successfully packed {rockspec_file} in {tmp}")
        else:
            print("Error while packing")
        # Find the generated .src.rock file
        rock_files = [f for f in listdir(temp_dir) if f.endswith(".src.rock")]
        if not rock_files:
            raise Exception("No .src.rock files found in the temporary directory.")
            return
        # Unpack the first .src.rock file found
        rock_prefix = rock_files[0]
        rock_file = join(tmp, rock_prefix)
        if (subprocess.run(["luarocks", "unpack", rock_file], cwd=temp_dir, check=True).returncode == 0):
            print(f"Successfully unpacked {rock_file} in {tmp}")
        else:
            print("Error while unpacking")
        # Get prefix of unpacked directory
        rock_prefix = rock_prefix[0 : -len(".src.rock")]
        # Get directory
        rock_dir = join(temp_dir, rock_prefix)
        # Find directories in rock_dir
        inner_dirs = [f for f in listdir(rock_dir) if isdir(join(rock_dir, f))]
        if not inner_dirs:
            raise Exception(f"No inner dir at path {rock_dir}")
        # Archive the first directory found
        inner_dir = join(rock_dir, inner_dirs[0])
        outfile = join(resultdir, rock_prefix + ".tar.gz")
        # create_tar_gz_with_prefix(inner_dir, rock_prefix, outfile)
        with tarfile.open(outfile, "w:gz") as tar:
            tar.add(inner_dir, arcname=rock_prefix)
        print(f"Successfully created {outfile}")
    args.outdir = outdir


class generate_rockspec(Generator):
    def __init__(self, *args, current_directory=GetCwd(), **kwargs):
        super().__init__(*args, **kwargs)
        self.session = Session()
        self.current_directory = current_directory
        self.get_session()

    # setup requests session
    def get_session(self):
        self.session.mount(
            "file://", FileAdapter(netloc_paths={".": self.current_directory})
        )
        self.session.mount("text://", TextAdapter())
        self.session.mount("stdin://", StdinAdapter())
        mount_adapter(self)

    # read rockspec file
    def read_rockspec_file(self, path_or_url):
        try:
            return self.session.get(path_or_url).text
        except RequestException:
            return open(path_or_url, "r").read()

    # function used for generating rockspec specification
    def rockspec(generator, args):
        # get rockspec path
        rockspec_path = args.rockspec
        luacode = args.luacode or []
        defines = args.define or []
        cache = {}
        newline = "\n"
        # generate lua code (luarocks rockspec contains an lua compatible code)
        luaprog = f"""
{newline.join(generator.read_rockspec_file(rockspec_path_i) for rockspec_path_i in rockspec_path)}
{os_specific_lua_code(args)}
{newline.join([cache[a]  for a in duplicates if custom_dependency(args, a, cache)] + luacode + [a[0] + '=' + a[1] for a in defines if len(a) >  1])}
"""
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
        filename = ( args.filename or rockspec.filename or generator.default_file_output(rockspec.name, template) )
        outdir = args.outdir or rockspec.outdir
        if outdir and isdir(outdir):
            chdir(outdir)
        mp = LuaMapping(rockspec)
        if is_enabled(args, "tostdout"):
            generator.render(mp, template)
        else:
            generator.write_template(mp, template, filename)


def custom_dependency(args, name, cache):
    try:
        array = getattr(args, name)
        if array is None:
            return False
    except AttributeError:
        return False
    if name not in cache:
        cache[name] = name + "={" + ",".join(map(repr, array)) + "}"
    return True


# Create requirement duplicates
duplicates = (
    lambda array, array2: ["add_" + i for i in array + array2] + ["add_luarocks_" + i for i in array]
)(
    (
        *map(
            lambda a: a + "_requires",
            (
                "build",
                "check",
                "preun",
                "pre",
                "postun",
                "post",
                "pretrans",
                "posttrans",
            ),
        ),
        "requires",
        "provides",
        "recommends",
        "conflicts",
        "obsoletes",
    ),
    ("patch", "source", "macro", "text"),
)

# Define generator's template environment
generator = generate_rockspec("lua2pack", __path__[0])


def Munch(args):
    import collections

    d = collections.defaultdict(lambda: None)
    d.update(args)
    return type(
        "Munch",
        tuple(),
        {
            "__getattr__": d.__getitem__,
            "__setattr__": d.__setitem__,
            "__getitem__": d.__getitem__,
            "__setitem__": d.__setitem__,
            "__contains__": d.__contains__,
        },
    )()


def main(args=None):
    # Create the parser
    mainparser = argparse.ArgumentParser(
        description="A Python script that generates a rockspec file"
    )
    # set defaults
    mainparser.set_defaults(func=lambda *a: mainparser.print_help())
    # add noop operation
    store_flag(mainparser, "noop")
    # add subparsers
    subparsers = mainparser.add_subparsers(title="commands")
    # add generate command
    parser = subparsers.add_parser(
        "generate",
        help="generate RPM spec or DEB dsc file for a rockspec specification",
    )
    # add generate command
    fetcher = subparsers.add_parser(
        "fetch", help="fetch sources for a rockspec specification"
    )
    # add noop operation
    store_flag(parser, "noop")
    store_flag(fetcher, "noop")
    # add tostdout flag
    store_flag(parser, "tostdout")
    store_flag(fetcher, "tostdout")
    # Define the command-line arguments
    # Rockspec file
    parser.add_argument(
        "--rockspec", help="Path to the rockspec file or URI", type=str, action="append"
    )
    fetcher.add_argument(
        "--rockspec", help="Path to the rockspec file or URI", type=str, action="append"
    )
    # Define lua parameters
    parser.add_argument(
        "--define",
        help="Override some lua parameters",
        type=str,
        action="append",
        nargs="*",
    )
    fetcher.add_argument(
        "--define",
        help="Override some lua parameters",
        type=str,
        action="append",
        nargs="*",
    )
    # Add specific lua code
    parser.add_argument(
        "--luacode", help="Override some lua codes", type=str, action="append"
    )
    fetcher.add_argument(
        "--luacode", help="Override some lua codes", type=str, action="append"
    )
    # Add duplicates
    for i in duplicates:
        parser.add_argument(
            "--" + i.replace("_", "-"),
            help=f"Additional {i.replace('_', ' ')[1:]} to be added",
            type=str,
            action="append",
        )
    os_specific_generate_args(parser)

    # Template file for generate command
    parser.add_argument(
        "-t", "--template", choices=generator.file_template_list(), help="file template"
    )
    # Template output filename for generate command
    parser.add_argument("-f", "--filename", help="output filename (optional)")
    # Template output directory for generate command
    parser.add_argument("--outdir", help="out directory (used by obs service)")
    fetcher.add_argument("--outdir", help="out directory (used by obs service)")
    # Function for generate command
    parser.set_defaults(func=generator)
    fetcher.set_defaults(func=fetch)
    # Parse arguments
    args = Munch(mainparser.parse_args(args).__dict__)
    # Check if noop is enabled, if yes, then exit
    if is_enabled(args, "noop"):
        return
    # Execute function
    args.func(args)


if __name__ == "__main__":
    main()
