# PyTower
High-level Python API for editing/generating Tower Unite maps

## Installation Instructions
1. Download Rust (latest nightly build): https://www.rust-lang.org/tools/install
2. (On Windows) Download Git Bash: https://git-scm.com/download/win
3. Ensure that `git` and `cargo` are added to the PATH environment variable. You can test this by running `git --version` and `cargo --version` in command line.
4. In the root repository directory, run `pip install .`

## Running PyTower
 - Once installed, PyTower can be run from command line as `pytower`
 - PyTower can also be run directly using `python -m pytower.tower`

Example usage:
 - `pytower --input CondoData --tool CreateImageAtlas`
 - `pytower --input CondoData --output TooledCondoData --tool Rescale -- 2`

### Program arguments
 - -i/--input: Input file to use (default: CondoData)
 - -o/--output: Output file to use (default: CondoData_output)
 - -t/--tool: Tool to use
 - -s/--select: Selection mode to use
 - -v/--invert: Flag to invert selection
 - -!/--overwrite: Flag overwrite output files
 - -j/--json: Flag to skip Suitebro parser steps

### Selection modes:
- ItemSelection (default): Everything except property-only objects (CondoSettingsManager_2, Ultra_Dynamic_Sky_##, CondoWeather_2729, etc.)
- NameSelection: Selects object by name (both custom name and internal object name)
- CustomNameSelection: Select objects by custom name (name assigned in game)
- ObjectNameSelection: Select objects by internal object name only
- GroupSelection: Select objects by group id
- RegexSelection: Select objects by regular expression pattern (matches both names) 

## Writing tools scripts
To register a new tool to use with PyTower, simply create a new script in the tools folder with a main method.

### Tooling script directives
- `TOOL_NAME`: Registers the name used by PyTower (by default it uses the script's file name)
- `VERSION`: Script version
- `AUTHOR`: Script author
- `URL`: External URL for more information (e.g., a link to a forum post)
- `IGNORE=True`: Tells PyTower to skip over this script. Useful for shared libraries or utility scripts