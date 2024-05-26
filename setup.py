from setuptools import setup

import conf

attrs={}

for i in dir(conf):
    if not i.startswith('_'):
        attrs[i] = getattr(conf, i)

setup(
 py_modules=['lua2pack'],
 install_requires=['jinja2-easy.generator', 'lupa'],
 **attrs
)
