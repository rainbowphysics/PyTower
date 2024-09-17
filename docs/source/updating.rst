Updating PyTower
================

Recommended Steps
-----------------
The best way to install PyTower is by using the command ``git clone https://github.com/rainbowphysics/PyTower.git``. This will create a clone of the Git repository insode of the current working directory. To change the current working directory, use the ``cd`` command, followed by the folder you'd like to install PyTower in. For example, ``cd C:\Users\myuser\Documents`` on Windows.

If PyTower is installed this way, using ``git clone``, then to update the repository from ``main`` all you need to do is run ``git pull`` in the main project directory. To use a specific version, run the command ``git checkout <VERSION>``, for example ``git checkout v0.1.0``. To go back to the latest release (i.e., the ``main`` branch of the repository), simply use ``git checkout main``. No reinstall is required while doing this because of how PyTower is installed as an editable ``pip`` package.

To summarize:
 - To download the repository, use ``git clone https://github.com/rainbowphysics/PyTower.git``
 - To update the repository, simply use ``git pull``

Alternative Installs
--------------------
Another way to update PyTower is to download the repository as a zip file from GitHub. From here, extract the archive to a folder and navigate to the main repository folder. When you run ``pip install -e .``, it will overwrite any previously installed ``pytower`` versions. 

For smaller updates, simply opening the zip file and dragging/dropping the contents to overwrite the files in your PyTower directory may work, but this is not recommended. Instead, if you'd like to do this, delete your pytower folder first (the main Python package folder with all the code, like ``tower.py``, ``suitebro.py``, etc.). Because the built-in tool script names do not change, this *should* work, but do this at your own discretion. 

If your ``pytower`` install breaks, simply download a fresh copy of PyTower (either through ``git clone`` or by downloading the zip file again) and run ``pip install -e .`` in the new install's main directory. This should overwrite preexisting package. If for some reason this fails, try running ``pip uninstall pytower`` before ``pip install -e .``, but ironically ``pip uninstall`` tends to fail more often than ``pip install`` does.
