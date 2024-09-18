.. tool_script_directives:
Tool Script Directives
======================

Tool script directives are special attributes read by PyTower when it parses a tool script. They help make tool scripts more presentable, user-friendly, and register metadata. All of them are optional, but recommended for accessibility.

List of directives:
 - ``TOOL_NAME``: Registers the name used by PyTower (by default it uses the script's file name)
 - ``VERSION``: Script version
 - ``AUTHOR``: Script author
 - ``URL``: External URL for more information (e.g., a link to a forum post)
 - ``INFO``: Further info printed when calling ``pytower info <toolname>``
 - ``PARAMETERS``: Dictionary of required parameters and their types (registered as ``ToolParameterInfo`` instances)
 - ``IGNORE=True``: Tells PyTower to skip over this script. Useful for shared libraries or utility scripts

By default ``PARAMETERS`` will be loaded as an empty dictionary. For examples involving the directives, `see the built-in tool scripts`__

.. _tools_scripts: https://github.com/rainbowphysics/PyTower/tree/main/tools
__ tools_scripts_

Example of PARAMETERS from rotate.py_ (as of v0.1.0):

.. _rotate.py: https://github.com/rainbowphysics/PyTower/tree/main/tools/rotate.py
.. code-block:: python
   PARAMETERS = {'rotation': ToolParameterInfo(dtype=xyz, description='Rotation to perform (in Euler angles and degrees)'),
                 'local': ToolParameterInfo(dtype=bool, description='Whether to only rotate locally', default=False)}


The ``{...}`` defines a Python dictionary (``dict``), where the parameter name is the key (``'rotation'``, ``'local'``) and the value is ``ToolParameterInfo(...)``. ``ToolParameterInfo`` is a class that registers information about each parameter. In the above example, ``rotation`` is registered as an ``xyz`` data type (input as ``x,y,z``) parameter with the description ``Rotation to perform (in Euler angles and degrees)``.

By default, each parameter in ``PARAMETERS`` is required. To make a parameter optional, the ``default`` argument must be passed to the ``ToolParameterInfo`` constructor. In the above example, ``'local'`` has the data type ``bool``, has the description ``Whether to only rotate locally``, and has the default value ``False``, which makes it an optional parameter.

To check that variable descriptions are formatted correctly, try running ``pytower info <TOOL_NAME>`` where ``<TOOL_NAME>`` is the ``TOOL_NAME`` of your tool script. ``URL`` and ``INFO`` are also displayed here in ``pytower info``.