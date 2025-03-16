#!/usr/bin/python3
# Import necessary modules
import lua2pack
from lua2pack import GetCwd
from lua2pack import osdeps
from lua2pack.osdeps import generic
from lua2pack import osdeps_utils
from lua2pack import generate_rockspec
import os
from lua2pack.osdeps import obsinfo
from luadata import serialize as sr
import sys


# Define the test spec content, that must be generated
if os.environ.get('GENERATE_TEST') != 'yes':
    try:
        test_spec_content = open('test_spec_content.txt','r').read()
    except Exception:
        test_spec_content = None
else:
    test_spec_content = False
# Define the test rockspec content
test_rockspec_content = r"""
package = "lua-cjson"
version = "2.1.0.11-1"

source = {
    url = "git+https://github.com/openresty/lua-cjson",
    tag = "2.1.0.11",
}

description = {
    summary = "A fast JSON encoding/parsing module",
    detailed = [[
        The Lua CJSON module provides JSON support for Lua. It features:
        - Fast, standards compliant encoding/parsing routines
        - Full support for JSON with UTF-8, including decoding surrogate pairs
        - Optional run-time support for common exceptions to the JSON specification
          (infinity, NaN,..)
        - No dependencies on other libraries]],
    homepage = "http://www.kyne.com.au/~mark/software/lua-cjson.php",
    license = "MIT"
}

dependencies = {
    "lua >= 5.1"
}

build = {
    type = "builtin",
    modules = {
        cjson = {
            sources = { "lua_cjson.c", "strbuf.c", "fpconv.c" },
            defines = {
-- LuaRocks does not support platform specific configuration for Solaris.
-- Uncomment the line below on Solaris platforms if required.
--                "USE_INTERNAL_ISINF"
            }
        },
        ["cjson.safe"] = {
            sources = { "lua_cjson.c", "strbuf.c", "fpconv.c" }
        }
    },
    install = {
        lua = {
            ["cjson.util"] = "lua/cjson/util.lua"
        },
        bin = {
            json2lua = "lua/json2lua.lua",
            lua2json = "lua/lua2json.lua",
        }
    },
    -- Override default build options (per platform)
    platforms = {
        win32 = { modules = { cjson = { defines = {
            "DISABLE_INVALID_NUMBERS", "USE_INTERNAL_ISINF"
        } } } }
    },
    copy_directories = { "tests" }
}

-- vi:ai et sw=4 ts=4:
"""

# Create a text test rockspec
text_test_rockspec = f'text://{test_rockspec_content}'

# Generate a rockspec using the test_case and lua2pack directory
generator = generate_rockspec('test_case', os.path.join(os.getcwd(), 'lua2pack'))


def remove_if_exists(name):
    if os.path.exists(name):
        os.remove(name)


def test_lua2pack_imports():
    # Test that the necessary modules can be imported
    remove_if_exists('lua-cjson-2.1.0.11-1.rockspec')
    remove_if_exists('lua-cjson.spec')
    remove_if_exists('lua-cjson.obsinfo')
    pass


class MappingTest(dict):
    # A custom dictionary class that allows attribute access
    def __init__(self, *a, **b):
        super().__init__(*a, **b)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return None

    def __setattr__(self, name, value):
        self[name] = value


def test_templates():
    # Test that the expected template files are generated
    files = generator.file_template_list()
    assert 'generic.spec' in files
    assert 'rock.rockspec' in files
    assert 'obs.obsinfo' in files


mtime = obsinfo.generate_timestamp()
commit = obsinfo.generate_random_hex()
obsinfo_text=f"""name: lua-cjson
version: 2.1.0.11-1
mtime: {str(mtime)}
commit: {commit}"""


def test_obsinfo_generated():
    # Test that the .obsinfo file is generated correctly
    a = MappingTest()
    # a - command line arguments object, parsed by argparse
    a.rockspec = [text_test_rockspec]
    a.define=[
        ['mtime', sr(mtime)],
        ['commit', sr(commit)],
        ['template',sr('obs.obsinfo')],
        ['filename','package..'+sr('.obsinfo')]
    ]
    generator(a)

    with open('lua-cjson.obsinfo','r') as read:
        assert read.read() == obsinfo_text


def test_rockspec_generated():
    # Test that the .rockspec file is generated correctly
    a = MappingTest()
    a.rockspec = [text_test_rockspec]
    a.template = 'rock.rockspec'
    generator(a)
    assert os.path.exists('lua-cjson-2.1.0.11-1.rockspec')

    a.template = 'generic.spec'
    a.name = 'lua-cjson'
    generator(a)

    with open('lua-cjson.spec','r') as read:
        spec_text1 = read.read()

    os.remove('lua-cjson.spec')
    a.rockspec = [ 'lua-cjson-2.1.0.11-1.rockspec' ]
    generator(a)

    with open('lua-cjson.spec','r') as read:
        spec_text2 = read.read()


    os.remove('lua-cjson.spec')
    a.rockspec = [ 'glob://./*-cjson-2.1.0.11-*.rockspec' ]
    generator(a)

    with open('lua-cjson.spec','r') as read:
        spec_text3 = read.read()

    if not test_spec_content:
        os.rename('lua-cjson.spec', 'test_spec_content.txt')
    else:
        assert spec_text1 == spec_text2 == spec_text3 == test_spec_content
    test_lua2pack_imports()


def test_noop():
    lua2pack.main(['generate', '--noop','enable'])
    lua2pack.main(['--noop','enable'])


if 'pytest' not in sys.modules:
    test_spec_content = None
    test_rockspec_generated()
