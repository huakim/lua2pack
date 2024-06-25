%define luarocks_pkg_name {{ package }}
%define luarocks_pkg_version {{ version }}
%define luarocks_pkg_prefix {{ prefix }}
%define luarocks_pkg_major {{ major }}
%define luarocks_pkg_minor {{ minor }}
{%- if not autogen %}
%global __luarocks_requires %{_bindir}/true
%global __luarocks_provides %{_bindir}/true
{%- endif %}

Name: {{ name }}
BuildRequires: lua-rpm-macros

%if %{defined luarocks_requires}
%luarocks_requires
%else
BuildRequires: %{lua_module luarocks}
BuildRequires: %{lua_module devel}
BuildRequires: gcc-c++
BuildRequires: gcc
BuildRequires: make
%endif
Version: %{luarocks_pkg_major}
Release: %{luarocks_pkg_minor}
Summary: {{ description.summary }}
Url: {{ description.homepage }}
License: {{ description.license }}
{%- if build.install.bin %}
Requires(postun): alternatives
Requires(post): alternatives
{%- endif %}

{%- if not autogen %}
Provides: %{luadist %{luarocks_pkg_name} = %{luarocks_pkg_version}}
{%- if not skip_build_dependencies %}
{%- for dep in dependencies %}
Requires: %{luadist {{ dependencies[dep] }}}
{%- endfor %}
{%- for dep in build_dependencies %}
BuildRequires: %{lua_module {{ build_dependencies[dep] }}}
{%- endfor %}
{%- endif %}
{%- else %}
BuildRequires: lua-generators
{%- endif %}

{%- for dep in add_luarocks_requires %}
Requires: %{luadist {{ add_luarocks_requires[dep] }}}
{%- endfor %}
{%- if not skip_build_dependencies %}
{%- for dep in add_luarocks_build_requires %}
BuildRequires: %{lua_module {{ add_luarocks_build_requires[dep] }}}
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
{%- for dep in add_requires %}
Requires: {{ add_requires[dep] }}
{%- endfor %}
{%- if not skip_build_dependencies %}
{%- for dep in add_build_requires %}
BuildRequires: {{ add_build_requires[dep] }}
{%- endfor %}
{%- endif %}
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

{%- if (((not autogen) and (test_dependencies)) or (add_check_requires) or (add_luarock_check_requires)) and (not skip_check_dependencies) %}
%if %{with check}
{%- if not autogen %}
{%- for dep in test_dependencies %}
BuildRequires: %{lua_module {{ test_dependencies[dep] }}}
{%- endfor %}
{%- endif %}
{%- for dep in add_check_requires %}
BuildRequires: {{ add_check_requires[dep] }}
{%- endfor %}
{%- for dep in add_luarocks_check_requires %}
BuildRequires: %{lua_module {{ add_luarocks_check_requires[dep] }}}
{%- endfor %}
%endif
{%- endif %}

Source0: {{ archive }}
Source1: {{ rockspec }}

{%- if autogen %}
%{?luarocks_generate_scriplets}
{%- endif %}

{%- if subpackages %}
%{?luarocks_subpackages{% if filelist %}:%luarocks_subpackages -f{% endif %}}
{%- endif %}

%description
{{ description.detailed }}

%prep
%autosetup -p1 -n %luarocks_pkg_prefix
%luarocks_prep

%generate_buildrequires
{%- if autogen and (not (skip_build_dependencies and skip_check_dependencies)) %}
%luarocks_generate_buildrequires{% if not skip_check_dependencies %} -t{% endif %}
{%- endif %}

%build
{%- if subpackages %}
%{?luarocks_subpackages_build}
%{!?luarocks_subpackages_build:%luarocks_build}
{%- else %}
%luarocks_build
{%- endif %}

%install
{%- if subpackages %}
%{?luarocks_subpackages_install}
%{!?luarocks_subpackages_install:%luarocks_install %{luarocks_pkg_prefix}.*.rock}
{%- else %}
%luarocks_install %{luarocks_pkg_prefix}.*.rock
{%- endif %}
{%- if filelist %}
%{?lua_generate_file_list}
{%- endif %}
%check
%if %{with check}
%{?luarocks_check}
%endif


{%- if not autogen_scriplets and build.install.bin %}
%post %{?lua_scriplets}
{%- for dep in build.install.bin %}
update-alternatives --install %{_bindir}/{{ dep }} {{ dep }} %{luarocks_treedir}/%{luarocks_pkg_name}/%{luarocks_pkg_version}/bin/{{ dep }} 25
{%- endfor %}
%postun %{?lua_scriplets}
{%- for dep in build.install.bin %}
update-alternatives --remove {{ dep }} %{luarocks_treedir}/%{luarocks_pkg_name}/%{luarocks_pkg_version}/bin/{{ dep }}
{%- endfor %}
{%- endif %}

%files %{?lua_files}{% if filelist %}%{!?lua_files:-f lua_files.list}{% endif %}
{%- if expected_files %}
{{ expected_files }}
{%- endif %}
