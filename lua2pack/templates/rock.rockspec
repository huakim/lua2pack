{%- if rockspec_format %}
rockspec_format = {{ __data_to_string(rockspec_format) }}
{%- endif %}
package = {{ __data_to_string(package) }}
version = {{ __data_to_string(version) }}
{%- if source %}
source = {{ __data_to_string(source) }}
{%- endif %}
{%- if description %}
description = {{ __data_to_string(description) }}
{%- endif %}
{%- if build %}
build = {{ __data_to_string(build) }}
{%- endif %}
{%- if supported_platforms %}
supported_platforms = {{ __data_to_string(supported_platforms) }}
{%- endif %}
{%- if dependencies %}
dependencies = {{ __data_to_string(dependencies) }}
{%- endif %}
{%- if build_dependencies %}
build_dependencies = {{ __data_to_string(build_dependencies) }}
{%- endif %}
{%- if external_dependencies %}
external_dependencies = {{ __data_to_string(external_dependencies) }}
{%- endif %}
{%- if test_dependencies %}
test_dependencies = {{ __data_to_string(test_dependencies) }}
{%- endif %}
