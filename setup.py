from setuptools import setup, find_packages


setup(
 name="lua2pack",
 version="0.0.1",
 packages=find_packages(),
 entry_points = {
    'console_scripts': [
       'lua2pack = lua2pack:main',
    ],
 },
 install_requires=['jinja2-easy.generator', 'lupa'],
)

