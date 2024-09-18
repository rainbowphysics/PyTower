Tool Scripts: Getting Started
=============================

General Information
-------------------
Tool scripts are located in the ``tools/`` folder. There are a dozen built-in tools, including ``tile.py``, ``set.py``, ``filter.py``, and ``scale.py``. To view a tool, simply open the file in a text-editor of your choice (I recommend Notepad++ or VSCode). When a script is added to ``tools/``, it is automatically indexed in ``tools-index.json`` and added to the list of tools. When it comes time to run the tool, its ``main`` function is executed by the core ``pytower`` program.

Tool Script Anatomy
-------------------
Tool scripts have the following general anatomy:
 - Python import statements (``import ...``, ``from ... import ...``)
 - Tooling directives (``TOOL_NAME``, ``AUTHOR``, ``PARAMETERS``, ...)
 - The main function (``def main(...):``)
 - Prototype mocking at the bottom (``if __name__ == '__main__': tower.run(...)``)

For more information about import statements in Python see: https://realpython.com/lessons/import-statement/

And for more information about the tooling directives currently available, see :ref:`Tool Script Directives <tool_script_directives>`

The main function is the most important part of the tooling script. It contains the Python code to actually be executed. It takes in the save data (as a ``Suitebro`` object), the active selection as a ``Selection`` set object, and any tool parameters (passed-through using ``-@`` or ``--parameters``) as a dictionary (``ParameterDict``).

As a full example, here are the contents of center.py_ (as of 0.1.0):

.. _center.py: https://github.com/rainbowphysics/PyTower/blob/main/tools/center.py

.. code-block:: python
   :linenos:

   # Python Imports
   from pytower import tower
   from pytower.selection import Selection
   from pytower.suitebro import Suitebro, TowerObject
   from pytower.tower import ToolParameterInfo, ParameterDict
   from pytower.util import xyz

   # PyTower Tool Directives
   TOOL_NAME = 'Center'
   VERSION = '1.0'
   AUTHOR = 'Physics System'
   URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/center.py'
   INFO = '''Centers selection at the world origin'''
   PARAMETERS = {'offset': ToolParameterInfo(dtype=xyz, description='Optional offset', default=xyz(0.0, 0.0, 0.0))}

   # Main function
   def main(save: Suitebro, selection: Selection, params: ParameterDict):
       offset = params.offset
       centroid = sum([obj.position for obj in selection]) / len(selection)

       for obj in selection:
           # Move so that the centroid becomes the origin
           obj.position -= centroid

           # Add optional offset
           obj.position += offset


   # If script is called directly: use tower.run to mock-run the tool
   if __name__ == '__main__':
       tower.run('CondoData', main, params=['offset=0,0,300'])


Where do I start?
-----------------
Making a tool script is as simple as taking copying a built-in tool and changing the details you want. You can even add code directly to tool scripts!

PyTower is designed to be as convenient and flexible as possible for artists and map-makers, so the best way to use the program is to copy a built-in tool or a recipe you like and start from there!

When you call ``pytower run`` it will automatically detect your script and add it to the index so it can be run at any point. Just make sure you give your script a unique ``TOOL_NAME``, or leave it blank to use the file name as a default



