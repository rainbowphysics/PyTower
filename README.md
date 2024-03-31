# PyTower 0.1.0
High-level Python API for editing/generating Tower Unite maps.

<p align="center">
  <img src="https://github.com/rainbowphysics/PyTower/blob/main/logo.png?raw=true" width="512" height="512" />
</p>

Discord community link: https://discord.gg/NUufVuu4Ve

## Installation Instructions
1. Download Rust (latest nightly build): https://www.rust-lang.org/tools/install
2. (On Windows) Download Git Bash: https://git-scm.com/download/win
3. Ensure that `git` and `cargo` are added to the PATH environment variable. You can test this by running `git --version` and `cargo --version` in command line.
4. Install Build Tools for Visual Studio (2017 or later): https://visualstudio.microsoft.com/downloads/?q=build+tools#build-tools-for-visual-studio-2022
5. In the root repository directory, run `pip install -e .`

## Running PyTower
 - Once installed, PyTower can be run from command line as `pytower`
 - PyTower can also be run directly using `python -m pytower.tower`
 - PyTower can also be imported into other Python projects with `import pytower`

## Current Issues
- Currently `run --select` and `run --invert` still need implementations, along with a few more of the `run` options. The current workaround is to modify the selection directly from within the tool scripts

### Available Subcommands:
 - `pytower help` 
 - `pytower version`
 - `pytower list`
 - `pytower info <TOOLNAME>` 
 - `pytower run <TOONAME> ...`

Example usage:
 - `pytower help`
 - `pytower info Tile`
 - `pytower run CreateImageAtlas --input CondoData`
 - `pytower run Rotate --output RotatedCondo --select group:4 -@ parameters rotation=0,0,45 local=true`

## `pytower run` arguments
 - -i/--input: Input file to use (default: CondoData)
 - -o/--output: Output file to use (default: CondoData_output)
 - -s/--select: Selection mode to use (default: `items`)
 - -v/--invert: Flag to invert selection
 - -j/--json: Flag to skip Suitebro parser steps
 - -@/--parameters: Beginning of *tool parameters*

### Tool parameter format:
 - Parameters are separated by spaces and have the format `param=value`
 - For example, `pytower run MyTool -@ offset=0,0,300 foo=42` passes two parameters to MyTool: `offset` with the value `xyz(0,0,300)` and `foo` with the value `42`.

### Selection modes:
- `items` (ItemSelector) (default): Everything except property-only objects (CondoSettingsManager_2, Ultra_Dynamic_Sky_##, CondoWeather_2729, etc.)`
- `name:<NAME>` (NameSelector): Selects object by name (both custom name and internal object name)
- `customname:<NAME>` (CustomNameSelector): Select objects by custom name (name assigned in game)
- `objname:<NAME>` (ObjectNameSelector): Select objects by internal object name only
- `group:<ID>` (GroupSelector): Select objects by group id
- `regex:<PATTERN>` (RegexSelector): Select objects by regular expression pattern (matches both custom name and object name)
- `everything`: Everything including property-only objects
- `nothing`: Nothing (can be useful for generation tools)

## Writing tools scripts
To register a new tool to use with PyTower, simply create a new script in the tools folder with a main method.

### Tooling script directives
- `TOOL_NAME`: Registers the name used by PyTower (by default it uses the script's file name)
- `VERSION`: Script version
- `AUTHOR`: Script author
- `URL`: External URL for more information (e.g., a link to a forum post)
- `INFO`: Further info printed when calling `pytower info <toolname>`
- `PARAMETERS`: Dictionary of required parameters and their types (registered as `ToolParameterInfo` instances)
- `IGNORE=True`: Tells PyTower to skip over this script. Useful for shared libraries or utility scripts

## Contributing
This project is open source and open to public contributions. 

To make a contribution, create a new branch/fork and submit a pull request. Contributions should follow the PEP 8 styleguide: https://peps.python.org/pep-0008/.

## Important Notice:
#### This API is not officially affiliated with PixelTail Games nor Tower Unite, please do not ask for help regarding tooling/scripts in the official Discord server nor on the official forums, except for in the megathread or in any other relevant threads.
#### Any tools/scripts posted or shared in this repository are not officially affiliated with PixelTail Games nor Tower Unite. They are unofficial tools created by the community for the purpose of making community content and maps.
#### Be safe when downloading tool scripts from the internet. Always look them over before adding them to the tools folder. If you can't understand how a tool script works, or if it looks sketchy, do not use it and report it.
