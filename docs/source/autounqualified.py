from sphinx.util import docstrings


def process_docstring(app, what, name, obj, options, lines):
    # Check if the object is a function
    if what == 'function':
        # Get the module name
        module_name = name.rsplit('.', maxsplit=1)[0]
        # Iterate through each line of the docstring
        for i, line in enumerate(lines):
            # Replace fully qualified function names with unqualified names
            lines[i] = lines[i].replace(module_name + '.', '')


def setup(app):
    app.connect('autodoc-process-docstring', process_docstring)
    return {'version': '0.1'}  # identifies the version of the extension
