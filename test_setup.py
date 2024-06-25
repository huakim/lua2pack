# Import necessary modules
import lua2pack
from lua2pack import osdeps
from lua2pack.osdeps import generic
from lua2pack import osdeps_utils
from lua2pack import generate_rockspec
import os
from lua2pack.osdeps import obsinfo
from luadata import serialize as sr

# Define the test spec content, that must be generated
test_spec_content = r"""%define luarock_pkg_name lua-cjson
%define luarock_pkg_version 2.1.0.11-1
%define luarock_pkg_prefix lua-cjson-2.1.0.11-1
%define luarock_pkg_major 2.1.0.11
%define luarock_pkg_minor 1
%global __luarock_requires %{_bindir}/true
%global __luarock_provides %{_bindir}/true

Name: lua-cjson
BuildRequires: luarocks-macros
BuildRequires: luarocks-subpackages-macros
%if %{defined luarock_requires}
%luarock_requires
%else
BuildRequires: lua-devel
%endif
Version: %{luarock_pkg_major}
Release: %{luarock_pkg_minor}
Summary: A fast JSON encoding/parsing module
Url: http://www.kyne.com.au/~mark/software/lua-cjson.php
License: MIT
Provides: %{luadist %{luarock_pkg_name} = %{luarock_pkg_version}}
Requires: %{luadist lua >= 5.1}

Source0: lua-cjson-2.1.0.11-1.tar.gz
Source1: lua-cjson-2.1.0.11-1.rockspec
%{?luarock_subpackages:%luarock_subpackages -f}

%description
        The Lua CJSON module provides JSON support for Lua. It features:
        - Fast, standards compliant encoding/parsing routines
        - Full support for JSON with UTF-8, including decoding surrogate pairs
        - Optional run-time support for common exceptions to the JSON specification
          (infinity, NaN,..)
        - No dependencies on other libraries

%prep
%autosetup -p1 -n %luarock_pkg_prefix
%luarocks_prep

%generate_buildrequires

%build
%{?luarocks_subpackages_build}
%{!?luarocks_subpackages_build:%luarocks_build}

%install
%{?luarocks_subpackages_install}
%{!?luarocks_subpackages_install:%luarocks_install %{luarock_pkg_prefix}.*.rock}
%{?lua_generate_file_list}
%check
%if %{with check}
%{?luarocks_check}
%endif
%post %{?lua_scriplets}
update-alternatives --install %{_bindir}/json2lua json2lua %{luarocks_treedir}/bin/json2lua 25
update-alternatives --install %{_bindir}/lua2json lua2json %{luarocks_treedir}/bin/lua2json 25
%postun %{?lua_scriplets}
update-alternatives --remove json2lua %{luarocks_treedir}/bin/json2lua
update-alternatives --remove lua2json %{luarocks_treedir}/bin/lua2json

%files %{?lua_files}%{!?lua_files:-f lua_files.list}"""

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
text_test_rockspec = f'text:{test_rockspec_content}'

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

    assert spec_text1 == spec_text2 == spec_text3 == test_spec_content
    test_lua2pack_imports()

#def test_spec_generated():
