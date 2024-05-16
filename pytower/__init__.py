r"""
########################
pytower (:mod:`pytower`)
########################

.. currentmodule:: pytower

Main module for PyTower.

API Modules
===========

Different modules involved in the API

.. autosummary::
   :toctree:
   :recursive:

   pytower.backup
   pytower.config
   pytower.copy
   pytower.mesh
   pytower.object
   pytower.selection
   pytower.suitebro
   pytower.tool_lib
   pytower.tower
   pytower.util
"""

__version__ = '0.3.0'

import os

root_directory = os.path.dirname(os.path.dirname(__file__))
