Fixing Canvases Using PyTower
=============================

Initial Installation
--------------------
Before anything, install PyTower using `these instructions`__ (also in README.md_)

.. _README.md : https://github.com/rainbowphysics/PyTower/blob/main/README.md
.. _install : https://pytower.readthedocs.io/en/latest/installation.html
__ install_

As of v0.2.0, it should be as easy as it gets to install PyTower

Instructions
------------
Verify PyTower Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Open command line by searching for "cmd" on your computer then hitting enter
2. Enter ``pytower version`` into command line
   - If PyTower is installed correctly, then it should print out "PyTower" followed by the installed version (e.g., "PyTower 0.2.0")

Setting Tower Unite install path in PyTower
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Open up your "steamapps" folder 
    - On Windows: C:\\Program Files (x86)\\Steam\\steamapps
    - On Linux: ~/.local/share/steamapps/
2. Navigate to the "common" folder, then "Tower Unite" folder
3. Copy this path (i.e., the path to the Tower Unite directory)
4. In command line, enter ``pytower config set tower_install_path <PATH>``

.. note::
   Alternatively, you can set the path in config.json within the PyTower install directory

Running ``pytower fix``
~~~~~~~~~~~~~~~~~~~~~~~
1. Navigate to your "Steam" folder, then to "userdata", your Steam ID3, "394690", "remote", and finally to "Condos"
   - From here, saves are organized by condo name and then by snapshot name. For example, C_SmoothDirt/CondoData is the currently active save for your Smooth Dirt condo. Meanwhile, WK_LevelEditor/cafe/CondoData would be the save for a snapshot called "cafe"
2. Open the folder of the save you want to fix canvases for and copy the path/address.
3. Enter ``cd <PATH>``, where ``<PATH>`` is the folder path/address pasted in 
   - If this worked, you should see the folder address followed by a ">" character
4. Type ``pytower fix <FILENAME>`` (i.e., "CondoData"), and hit enter 
5. From here, PyTower will automatically detect broken canvases and attempt to reupload them to Catbox
   - If this process succeeds, you should see "Successfully reuploaded XXX/XXX to Catbox!"
6. Open the map in Tower Unite as usual, and hopefully all of your canvases are now fixed!

**Happy mapping and condo building!!!** 💖

Troubleshooting
---------------
"Marked 0/### files for reupload" or "XXX is online but returned status code: ###"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- PyTower tries to automatically determine whether or not a file is still available
   - Sometimes this will cause PyTower to think a resource is still available when it actually isn't
- **Solution**: Use the ``--force`` flag, which will force a reupload of all files: ``pytower fix <FILENAME> --force``

"Error while uploading file: HTTPSConnectionPool(host='catbox.moe', port=443): Max retries exceeded [...]"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Catbox is the default backend PyTower tries to use for uploading images
- In some countries Catbox is blocked, and may be blocked by default by your antivirus
   - This is because some capacity, Catbox is an image host for 4chan. However, it doesn't seem to be funded by 4chan directly at all, instead all the money comes from a Patreon. Whatever the connection is, at least it's not being funded by AI techbros trying to scrape your data
- **Solution**: Add an antivirus exclusion for Catbox or use a VPN.
   - Alternatively try using the imgur backend with ``--backend imgur`` or try `making your own custom backend`__
- If this doesn't work then it's possible that the Catbox servers are down for maintenance: check https://status.catbox.moe/

.. _custom : https://github.com/rainbowphysics/PyTower/blob/main/pytower/image_backends/custom.py
__ custom_