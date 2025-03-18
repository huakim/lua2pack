Lua2pack: Generate distribution packages from `Luarocks`_
=================================================

.. image:: https://github.com/huakim/lua2pack/actions/workflows/python-package.yml/badge.svg
        :target: https://github.com/huakim/lua2pack/actions/workflows/python-package.yml
        :alt: Unit tests

This script allows to generate RPM spec files from `Luarocks`_.


Installation
------------

To install lua2pack from the `Python Package Index`_, simply:

.. code-block:: bash

    $ python3 -mpip install lua2pack

You can also check your distro of choice if they provide packages.

Usage
-----

Lets suppose you want to package luarock named `path`_. 
First of all, you can download rockspec file
and fetch source

.. code-block:: bash

    $ luarocks download --rockspec path 
    
    $ lua2pack fetch --rockspec 'glob://./*.rockspec'
    Cloning into 'lua-path'...
    remote: Enumerating objects: 288, done.
    remote: Total 288 (delta 0), reused 0 (delta 0), pack-reused 288 (from 1)
    Receiving objects: 100% (288/288), 33.78 KiB | 6.76 MiB/s, done.
    Resolving deltas: 100% (155/155), done.
    Note: switching to '35f8e6b0e8f9a735ecc5b4834147fad83e42851d'.

    You are in 'detached HEAD' state. You can look around, make experimental
    changes and commit them, and you can discard any commits you make in this
    state without impacting any branches by switching back to a branch.

    If you want to create a new branch to retain commits you create, you may
    do so (now or later) by using -c with the switch command. Example:

      git switch -c <new-branch-name>

    Or undo this operation with:

      git switch -

    Turn off this advice by setting config variable advice.detachedHead to false

    Packed: /tmp/tmp9utki30_/path-1.1.0-1.src.rock
    Successfully packed /tmp/tmp9utki30_/path-1.1.0-1.rockspec in /tmp/tmp9utki30_

    Done. You may now enter directory 
    path-1.1.0-1/lua-path
    and type 'luarocks make' to build.
    Successfully unpacked /tmp/tmp9utki30_/path-1.1.0-1.src.rock in /tmp/tmp9utki30_
    Successfully created /extra/home/suse/Desktop/path-1.1.0-1.tar.gz


As a next step you may want to generate a package recipe for your distribution.
For RPM_-based distributions you want to
generate a spec file (named 'lua-path.spec'):

.. code-block:: bash

    $ lua2pack generate --rockspec 'glob://./*.rockspec' --template 'generic.spec'

The source tarball and the package recipe is all you need to generate the RPM_
(or DEB_) file.
This final step may depend on which distribution you use. 
For building source rpm file the complete recipe is:

.. code-block:: bash

    $ rpmbuild -bs "-D_sourcedir $PWD" lua-path.spec
    ...

Depending on the module, you may have to adapt the resulting spec file slightly.
To get further help about lua2pack usage, issue the following command:

.. code-block:: bash

    $ lua2pack --help


Hacking and contributing
------------------------

You can test lua2pack from your git checkout by executing the lua2pack module.

Edit `setup.py` file changing the version number.
From the lua2pack directory, install the lua2pack module locally.

.. code-block:: bash

    $ pip install -e .

Now you can run your hackish lua2pack version. It is usually located in
$HOME/.local/bin/lua2pack

.. code-block:: bash

    $ lua2pack

Fork `the repository`_ on Github to start making your changes to the **master**
branch (or branch off of it). Don't forget to write a test for fixed issues or
implemented features whenever appropriate. You can invoke the testsuite from
the repository root directory via `tox`_:

.. code-block:: bash

    $ tox


You can also run `pytest`_ directly:

.. code-block:: bash

    $ pytest

It assumes you have the test dependencies installed (available on PYTHONPATH)
on your system.

:copyright: (c) 2021 huakim tylyktar.
:license: Apache-2.0, see LICENSE for more details.


.. _argparse: http://pypi.python.org/pypi/argparse
.. _Jinja2: http://pypi.python.org/pypi/Jinja2
.. _Luarocks: https://luarocks.org
.. _path: https://luarocks.org/modules/mah0x211/path
.. _RPM: http://en.wikipedia.org/wiki/RPM_Package_Manager
.. _DEB: http://en.wikipedia.org/wiki/Deb_(file_format)
.. _`Python Package Index`: https://pypi.org/
.. _`the repository`: https://github.com/huakim/lua2pack
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: http://testrun.org/tox
