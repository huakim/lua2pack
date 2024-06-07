from setuptools import setup, find_packages


setup(
 name="lua2pack",
 version="0.0.5",
 description = "Generate RPM or DSC spec files from luarocks",
 summary = "This utility is used for generating files of specific template from luarocks",
 license = "GPLv3",
 url = "https://github.com/huakim/lua2pack",
 packages=find_packages(),
 entry_points = {
    'console_scripts': [
       'lua2pack = lua2pack:main',
    ],
 },
 install_requires=['jinja2-easy.generator', 'lupa'],
)

