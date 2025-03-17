%define luarocks_pkg_name {{ package }}
%define luarocks_pkg_version {{ version }}
%{?!luadist:%define luadist(-) lua}
Source1: {{ rockspec }}
%define luarocks_rockspec_file %{SOURCE1}
Name: {{ name }}
Version: {{ major }}
Release: {{ minor }}%{?autorelease}
Summary: {{ description.summary or 'FIXME: Summary is missing' }}
Url: {{ description.homepage or 'https://fix.me/homepage/is/missing' }}
License: {{ description.license or 'FIXME: License is missing' }}
Source0: {{ archive }}
BuildRequires: lua-rpm-macros
BuildRequires: luarocks-macros
Requires(postun): alternatives
Requires(post): alternatives
Provides: %{luadist %{luarocks_pkg_name} = %{luarocks_pkg_version}}
{%- if noarch %}
BuildArch: noarch
{%- endif %}
{%- for dep in add_source %}
Source{{ str(int(dep) + 1) }}: {{ add_source[dep] }}
{%- endfor %}
{%- for dep in add_patch %}
Patch{{ str(int(dep) - 1) }}: {{ add_patch[dep] }}
{%- endfor %}
{%- for dep in add_macro %}
%define {{ add_macro[dep] }}
{%- endfor %}
{%- for dep in add_text %}
{{ add_text[dep] }}
{%- endfor %}
{%- if not autoreqs %}
%global __luarocks_requires %{_bindir}/true
%global __luarocks_provides %{_bindir}/true
{%- for dep in dependencies %}
Requires: %{luadist {{ dependencies[dep] }}}
{%- endfor %}
{%- endif %}
{%- for dep in add_luarocks_preun_requires %}
Requires(preun): %{luadist {{ add_luarocks_preun_requires[dep] }}}
{%- endfor %}
{%- for dep in add_luarocks_postun_requires %}
Requires(postun): %{luadist {{ add_luarocks_postun_requires[dep] }}}
{%- endfor %}
{%- for dep in add_luarocks_pretrans_requires %}
Requires(pretrans): %{luadist {{ add_luarocks_pretrans_requires[dep] }}}
{%- endfor %}
{%- for dep in add_luarocks_posttrans_requires %}
Requires(posttrans): %{luadist {{ add_luarocks_posttrans_requires[dep] }}}
{%- endfor %}
{%- for dep in add_luarocks_pre_requires %}
Requires(pre): %{luadist {{ add_luarocks_pre_requires[dep] }}}
{%- endfor %}
{%- for dep in add_luarocks_post_requires %}
Requires(post): %{luadist {{ add_luarocks_post_requires[dep] }}}
{%- endfor %}
{%- for dep in add_luarocks_provides %}
Provides: %{luadist {{ add_luarocks_provides[dep] }}}
{%- endfor %}
{%- for dep in add_luarocks_recommends %}
Recommends: %{luadist {{ add_luarocks_recommends[dep] }}}
{%- endfor %}
{%- for dep in add_luarocks_conflicts %}
Conflicts: %{luadist {{ add_luarocks_conflicts[dep] }}}
{%- endfor %}
{%- for dep in add_luarocks_obsoletes %}
Obsoletes: %{luadist {{ add_luarocks_obsoletes[dep] }}}
{%- endfor %}
{%- for dep in add_requires %}
Requires: {{ add_requires[dep] }}
{%- endfor %}
{%- for dep in add_preun_requires %}
Requires(preun): {{ add_preun_requires[dep] }}
{%- endfor %}
{%- for dep in add_postun_requires %}
Requires(postun): {{ add_postun_requires[dep] }}
{%- endfor %}
{%- for dep in add_pre_requires %}
Requires(pre): {{ add_pre_requires[dep] }}
{%- endfor %}
{%- for dep in add_post_requires %}
Requires(post): {{ add_post_requires[dep] }}
{%- endfor %}
{%- for dep in add_pretrans_requires %}
Requires(pretrans): {{ add_pretrans_requires[dep] }}
{%- endfor %}
{%- for dep in add_posttrans_requires %}
Requires(posttrans): {{ add_posttrans_requires[dep] }}
{%- endfor %}
{%- for dep in add_provides %}
Provides: {{ add_provides[dep] }}
{%- endfor %}
{%- for dep in add_recommends %}
Recommends: {{ add_recommends[dep] }}
{%- endfor %}
{%- for dep in add_conflicts %}
Conflicts: {{ add_conflicts[dep] }}
{%- endfor %}
{%- for dep in add_obsoletes %}
Obsoletes: {{ add_obsoletes[dep] }}
{%- endfor %}
{%- if not autobuildreqs %}
%if %{defined luarocks_buildrequires}
BuildRequires: %{luarocks_buildrequires}
%endif
{%- if not skip_build_dependencies %}
{%- for dep in build_dependencies %}
BuildRequires: %{lua_module {{ build_dependencies[dep] }}}
{%- endfor %}
{%- for dep in add_luarocks_build_requires %}
BuildRequires: %{lua_module {{ add_luarocks_build_requires[dep] }}}
{%- endfor %}
{%- for dep in add_build_requires %}
BuildRequires: {{ add_build_requires[dep] }}
{%- endfor %}
{%- endif %}
{%- if (not skip_check_dependencies) and (test_dependencies or add_check_requires or add_luarocks_check_requires) %}
%if %{with check}
{%- for dep in test_dependencies %}
BuildRequires: %{lua_module {{ test_dependencies[dep] }}}
{%- endfor %}
{%- for dep in add_luarocks_check_requires %}
BuildRequires: %{lua_module {{ add_luarocks_check_requires[dep] }}}
{%- endfor %}
{%- for dep in add_check_requires %}
BuildRequires: {{ add_check_requires[dep] }}
{%- endfor %}
%endif
{%- endif %}
{%- endif %}
{%- if subpackages %}
%{?luarocks_subpackages{% if filelist %}:%luarocks_subpackages -f{% endif %}}
%{?!luarocks_subpackages:Provides: luadist(%{luarocks_pkg_name}) = %{luarocks_pkg_version}}
{%- else %}
Provides: luadist(%{luarocks_pkg_name}) = %{luarocks_pkg_version}
{%- endif %}

%description
{{ description.detailed }}

%prep
%autosetup -p1 -n %{luarocks_pkg_prefix}
%luarocks_prep
{%- if autobuildreqs %}

%generate_buildrequires
%{?luarocks_buildrequires_echo}
{%- if not skip_check_dependencies %}
%if %{with check}
%luarocks_generate_buildrequires -c {% if not skip_build_dependencies %}-b{% endif %}
{% if not skip_build_dependencies %}%else{% endif %}
{%- endif %}
{% if not skip_build_dependencies %}%luarocks_generate_buildrequires -b {% endif %}
{%- if not skip_check_dependencies %}
%endif
{%- endif %}
{%- if not skip_build_dependencies %}
{%- for dep in add_luarocks_build_requires %}
%{lua_module_echo {{ add_luarocks_build_requires[dep] }}}
{%- endfor %}
{%- for dep in add_build_requires %}
echo {{ add_build_requires[dep] }}
{%- endfor %}
{%- endif %}
{%- if (not skip_check_dependencies) and (test_dependencies or add_check_requires or add_luarocks_check_requires) %}
%if %{with check}
{%- for dep in add_luarocks_check_requires %}
%{lua_module_echo {{ add_luarocks_check_requires[dep] }}}
{%- endfor %}
{%- for dep in add_check_requires %}
echo {{ add_check_requires[dep] }}
{%- endfor %}
%endif
{%- endif %}
{%- endif %}

%build
%{?custom_build}
{%- if subpackages %}
%if %{defined luarocks_subpackages_build}
%{luarocks_subpackages_build}
%else
{%- endif %}
%if %{defined luarocks_pkg_build}
%luarocks_pkg_build %{lua_version}
%else
%luarocks_build_luaver %{lua_version}
%endif
{%- if subpackages %}
%endif
{%- endif %}

%install
%{?custom_install}
{%- if subpackages %}
%if %{defined luarocks_subpackages_install}
%{luarocks_subpackages_install}
%else
{%- endif %}
%if %{defined luarocks_pkg_install}
%luarocks_pkg_install %{lua_version}
%else
%luarocks_install_luaver %{lua_version}
%endif
{%- if subpackages %}
%endif
{%- endif %}

{%- if filelist %}
%{?lua_generate_file_list}
{%- endif %}

%check
%if %{with check}
%{?luarocks_check}
%endif

{%- if not autoalternatives %}
{%- if build.install.bin %}
%post %{?lua_scriplets}
{%- for dep in build.install.bin %}
%add_lua_binary {{ dep }} -p 25 -b %{_bindir}
{%- endfor %}
%postun %{?lua_scriplets}
{%- for dep in build.install.bin %}
%drop_lua_binary {{ dep }}
{%- endfor %}
{%- endif %}
{%- else %}
%post %{?lua_scriplets}
%scan_and_add_lua_binaries
%postun %{?lua_scriplets}
%scan_and_drop_lua_binaries
{%- endif %}

%files %{?lua_files}{% if filelist %}%{!?lua_files:-f lua_files.list}{% endif %}
{%- if expected_files %}
{{ expected_files }}
{%- endif %}
