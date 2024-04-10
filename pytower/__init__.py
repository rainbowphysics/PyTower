__version__ = '0.2.0'

from scoping import scoping

# Scope so that pytower doesn't always import os
with scoping():
    import os

    root_directory = os.path.dirname(os.path.dirname(__file__))
    scoping.keep('root_directory')

del scoping
