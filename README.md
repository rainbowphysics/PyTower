# PyTower 
A high-level Python API for editing/generating Tower Unite maps

<p align="center">
  <img src="https://github.com/rainbowphysics/PyTower/blob/main/logo.png?raw=true" width="512" height="512" />
</p>

Discord community link: https://discord.gg/NUufVuu4Ve

## Dependencies
 - Python 3.10+

## Quick Installation
1. Download the install-pytower script from latest release
2. Run the installer script from command line using Python. For example, `python install-pytower-v0.2.0.py`
3. Follow the installation instructions and enjoy using PyTower!

## Recommened Installation Instructions
1. (On Windows) Install Git Bash: https://git-scm.com/download/win. 
2. Clone the repository using `git clone https://github.com/rainbowphysics/PyTower.git`. If typing `git` into the command line does nothing, you may have to add git manually to your PATH environment variable.
3. In the root repository directory, run `pip install -e .`. Note that the `-e` flag is important and the install will break without it

## Running PyTower
 - Once installed, PyTower can be run from command line as `pytower`
 - PyTower can also be run directly using `python -m pytower.tower`
 - PyTower can also be imported into other Python projects with `import pytower`

### Available Subcommands:
 - `pytower help`: General help page
 - `pytower version`: PyTower version
 - `pytower convert`: Convert between CondoData and .json
 - `pytower backup`: (WIP) Canvas backup tool
 - `pytower scan <PATH>`: Scans path/directory for tool scripts
 - `pytower list`: List all detected tools
 - `pytower info <TOOLNAME>`: Get detailed information about `<TOOLNAME>` 
 - `pytower run <TOONAME> ...`: Run tool
 - `pytower config`: (WIP) Access config

Example usage:
 - `pytower help`: Displays help about PyTower
 - `pytower info Tile`: Gets advanced info/help for tool "Tile"
 - `pytower scan .`: Scans current directory for tool scripts to add
 - `pytower run Rotate --output RotatedCondo --select group:4 -@ rotation=0,0,45 local=true`: Runs the "Rotate" tool with a group selection and passed-through parameters

## `pytower run` arguments
 - -i/--input: Input file to use (default: CondoData)
 - -o/--output: Output file to use (default: CondoData_output)
 - -s/--select: Selection mode to use (default: `items`)
 - -v/--invert: Flag to invert selection
 - -j/--json: Flag to skip Suitebro parser steps
 - -g/--per-group: Flag to apply the tool separately per group
 - -@/--parameters: Beginning of *tool parameters*

### Tool parameter format:
 - Parameters are separated by spaces and have the format `param=value`
 - For example, `pytower run MyTool -@ offset=0,0,300 foo=42` passes two parameters to MyTool: `offset` with the value `xyz(0,0,300)` and `foo` with the value `42`.

### Selection modes:
- `items` (default): Everything except property-only objects (CondoSettingsManager_2, Ultra_Dynamic_Sky_##, CondoWeather_2729, etc.)`
- `name:<NAME>`: Selects object by name (both custom name and internal object name)
- `customname:<NAME>`: Select objects by custom name (name assigned in game)
- `objname:<NAME>`: Select objects by internal object name only
- `group:<ID>`: Select objects by group id
- `regex:<PATTERN>`: Select objects by regular expression pattern (matches both custom name and object name)
- `all`: Everything including property-only objects
- `none`: Nothing (can be useful for generation tools)

## Writing tools scripts
To register a new tool to use with PyTower, simply create a new script in the tools folder with a main method.

### Tooling script directives
- `TOOL_NAME`: Registers the name used by PyTower (by default it uses the script's file name)
- `VERSION`: Script version
- `AUTHOR`: Script author
- `URL`: External URL for more information (e.g., a link to a forum post)
- `INFO`: Further info printed when calling `pytower info <toolname>`
- `PARAMETERS`: Dictionary of required parameters and their types (registered as `ToolParameterInfo` instances)
- `HIDDEN=True`: Tells PyTower to hide and skip over this script. Useful for shared libraries

## Contributing
This project is open source and open to public contributions. 

To make a contribution, create a new branch/fork and submit a pull request. Contributions should follow the PEP 8 styleguide: https://peps.python.org/pep-0008/.

## Important Notice:
#### This API is not officially affiliated with PixelTail Games nor Tower Unite, please do not ask for help regarding tooling/scripts in the official Discord server nor on the official forums, except for in the megathread or in any other relevant threads.
#### Any tools/scripts posted or shared in this repository are not officially affiliated with PixelTail Games nor Tower Unite. They are unofficial tools created by the community for the purpose of making community content and maps.
#### Be safe when downloading tool scripts from the internet. Always look them over before adding them to the tools folder. If you can't understand how a tool script works, or if it looks sketchy, do not use it and report it.
