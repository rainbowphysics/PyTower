# PyTower
High-level Python API for editing/generating Tower Unite maps

## Installation Instructions
1. Download Rust (latest nightly build): https://www.rust-lang.org/tools/install
2. (On Windows) Download Git Bash: https://git-scm.com/download/win
3. In the root repository directory, run `pip install .`

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