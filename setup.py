from setuptools import setup, find_packages
name='lua2pack'
setup(
      name="lua2pack",
      package_data={'': ['lua2pack/templates/*']},
      include_package_data=True,
      version="1.0.16",
      description = "Generate RPM or DSC spec files from luarocks",
      summary = "This utility is used for generating files of specific template from luarocks",
      license = "GPLv3",
      url = "https://github.com/huakim/lua2pack",
      packages=find_packages(),
      entry_points = {
         'console_scripts': [
            'lua2pack = lua2pack:main'
         ],
      },
      install_requires=[
#	'jinja2-easy.generator',
	'lupa',
'luadata',#	'luadata.luatable',
	'toposort',
	'platformdirs',
	'jinja2',
	'requests',
'sortedcontainers', 'glob2'#	'requests-glob',
#	'requests-text',
#	'requests-stdin'
],
)
