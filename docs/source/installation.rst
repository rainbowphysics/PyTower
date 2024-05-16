Installation Guide & Troubleshooting
====================================

PyTower currently has the following dependencies: cargo, git, and pip.

Within Python, PyTower has a few dependencies that are automatically installed (such as requests, numpy, and scipy)

.. _dependencies:

Dependencies
------------
 - Python 3.10+
 - (Included in /lib): tower-unite-suitebro_ by brecert
 - (Automatically installed by pip): numpy, scipy, requests, colorama, and any other Python packages in requirements.txt

.. _tower-unite-suitebro: https://github.com/brecert/tower-unite-suitebro

.. _quick_install:

Quick Installation
------------------
1. Download the ``install-pytower.py`` script from latest release
2. Run the installer script from command line using Python. For example, ``python install-pytower-v0.2.0.py``.

.. note::

   Alternatively, (on Windows) you can drag the install script onto python.exe or otherwise open the install script with python.exe

.. _recommended_install:

Recommended Installation Instructions
-------------------------------------
1. (On Windows) Install Git Bash: https://git-scm.com/download/win.

2. Clone the repository using ``git clone https://github.com/rainbowphysics/PyTower.git``.

.. note::

   If typing ``git`` into the command line does nothing, you may have to add git manually to your PATH environment variable.

3. Run ``install.bat`` (on Windows) or ``install.sh`` (on Linux).

.. note::

   Alternatively, directly run ``pip install -e .``. (``-e`` flag must be included, install will break without it!)


Installing From Source
----------------------
If for some reason you want to build the suitebro parser from source (as opposed to using the lib), you can use the flag ``--install-option="--src"``.

.. code-block:: console

   $ pip install -e . --install-option="--src"

Note that this requires the latest version of Rust be installed, along with Build Tools for Visual Studio (2017) and Git Bash on Windows.

Once you've done this, you also have to configure PyTower to use suitebro parser source with:

.. code-block:: console

   $ pytower config set from_source true
