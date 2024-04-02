import argparse
import collections
import importlib
import pkgutil  # properly imports importlib.util for some reason
import json
import logging
import os
import sys
from subprocess import Popen, PIPE
from types import ModuleType
from typing import Callable

import numpy as np

from . import __version__, root_directory
from .selection import *
from .suitebro import Suitebro
from .util import xyz, xyzint, xyz_to_string

# _active_saves is a stack
_active_saves: list[Suitebro] = []


def get_active_save() -> Suitebro:
    return _active_saves[-1] if len(_active_saves) > 0 else None


def run_suitebro_parser(input_path: str, to_save: bool, output_path: str | None = None, overwrite: bool = False):
    curr_cwd = os.getcwd()
    suitebro_path = os.path.join(root_directory, 'tower-unite-suitebro')
    os.chdir(suitebro_path)
    
    process = Popen(f'cargo run --release {"to-save" if to_save else "to-json"} {"-!" if overwrite else ""}'
                    f' -i \"{input_path}\" -o \"{output_path}\"', stdout=PIPE, shell=True)
    (output, err) = process.communicate()
    #print(output, file=sys.stderr)
    for line in output.splitlines(False):
        print(line.decode('ascii'))

    exit_code = process.wait()

    if exit_code != 0:
        logging.warning('Suitebro to-json did not complete successfully!')

    os.chdir(curr_cwd)


class ToolParameterInfo:
    def __init__(self, dtype: Callable = str, description='', default=None):
        self.dtype = dtype
        self.description = description
        self.default = default

    def to_dict(self) -> dict:
        data = {}
        data['dtype'] = self.dtype.__name__
        data['description'] = self.description

        if self.default is not None and (self.dtype == xyz or self.dtype == xyzint):
            data['default'] = xyz_to_string(self.default)
        else:
            data['default'] = self.default
        return data

    @staticmethod
    def from_dict(data: dict) -> 'ToolParameterInfo':
        # Define conversion to/from registered parameter types
        type_table = {'str': str, 'bool': bool, 'int': int, 'float': float, 'xyz': xyz, 'xyzint': xyzint}

        # Load values
        dtype = type_table[data['dtype']]
        description = data['description']
        default = dtype(data['default']) if 'default' in data and data['default'] is not None else None

        return ToolParameterInfo(dtype, description, default)


class ToolMetadata:
    def __init__(self, tool_name: str, params: dict[str, ToolParameterInfo], version: str, author: str, url: str,
                 info: str):
        self.tool_name = tool_name
        self.params = params
        self.version = version
        self.author = author
        self.url = url
        self.info = info

    def get_info(self) -> str:
        info_str = f'{self.tool_name} Information:'

        for var, value in vars(self).items():
            if var in ['version', 'author'] and value is not None:
                info_str += f'\n  {var.capitalize()}: {value}'

        if self.url is not None:
            info_str += f'\n  URL: {self.url}'

        if self.info is not None:
            info_str += f'\n\n{self.info}'

        if self.params:
            param_str = '\n\nParameters:'
            for name, info in self.params.items():
                param_str += f'\n  {name}:{info.dtype.__name__} - {info.description}'
                if info.default is not None:
                    param_str += f' (default: {info.default})'

            info_str += param_str

        return info_str

    @staticmethod
    def attr_or_default(module, attr, default):
        if hasattr(module, attr):
            return getattr(module, attr)

        return default

    @staticmethod
    def strattr_or_default(module, attr, default):
        if hasattr(module, attr):
            return str(getattr(module, attr)).strip()

        return default

    def to_dict(self) -> dict:
        data = {varname: value for (varname, value) in vars(self).items() if varname != 'params' and value is not None}

        # Special handling for parameters
        data['params'] = {}  # Need fresh dictionary, make sure pointers dont get shared
        for p_name, p_info in self.params.items():
            data['params'][p_name] = p_info.to_dict()

        return data

    @staticmethod
    def from_dict(data: dict) -> 'ToolMetadata':
        # Convert the input dict into a defaultdict so that missing entries become None
        data_or_none = collections.defaultdict(lambda: None, data)
        tool_name = data_or_none['tool_name']
        version = data_or_none['version']
        author = data_or_none['author']
        url = data_or_none['url']
        info = data_or_none['info']

        # Handle parameter list
        params = data_or_none['params']
        for p_name, p_info_dict in params.items():
            params[p_name] = ToolParameterInfo.from_dict(p_info_dict)

        return ToolMetadata(tool_name, params, version, author, url, info)


class ParameterDict(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        else:
            raise AttributeError(f"'ParameterDict' object has no attribute '{key}'")


ToolMainType = Callable[[Suitebro, Selection, ParameterDict], None]
ToolListType = list[tuple[ModuleType, ToolMetadata]]
PartialToolListType = list[tuple[ModuleType | str, ToolMetadata]]


def load_tool(script_path, verbose=True) -> tuple[ModuleType, ToolMetadata] | None:
    script = os.path.basename(script_path)
    module_name = os.path.splitext(script)[0]
    if verbose:
        print(f"Loading tool script: {module_name}")
    try:
        # TODO convert from importlib.util to pkgutil
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check if module should be ignored before proceeding
        if hasattr(module, 'IGNORE') and getattr(module, 'IGNORE'):
            return None

        # Get script directives/metadata variables
        tool_name = ToolMetadata.strattr_or_default(module, 'TOOL_NAME', module_name)
        params = ToolMetadata.attr_or_default(module, 'PARAMETERS', {})
        version = ToolMetadata.strattr_or_default(module, 'VERSION', None)
        author = ToolMetadata.strattr_or_default(module, 'AUTHOR', None)
        url = ToolMetadata.strattr_or_default(module, 'URL', None)
        info = ToolMetadata.strattr_or_default(module, 'INFO', None)

        # Check if the module has a main function before registering it
        if not hasattr(module, 'main') and verbose:
            logging.warning(f"No 'main' function found in tool '{tool_name}'. Skipping.")
            return None

        if verbose:
            success_message = f'Successfully loaded {tool_name}'
            if version is not None:
                success_message += f' {version}'
            if author is not None:
                success_message += f' by {author}'
            logging.info(success_message)

        return module, ToolMetadata(tool_name, params, version, author, url, info)

    except Exception as e:
        logging.error(f"Error loading tool '{script}': {e}")


TOOLS_PATH = os.path.join(root_directory, 'tools')
TOOLS_INDEX_NAME = 'tools-index.json'
TOOLS_INDEX_PATH = os.path.join(root_directory, TOOLS_INDEX_NAME)


def make_tools_index(tools: PartialToolListType):
    tools_dict = {}
    for module_or_path, meta in tools:
        # Convert tool metadata to dictionary
        tool_data = meta.to_dict()

        # Get path name
        if isinstance(module_or_path, ModuleType):
            tool_path = module_or_path.__file__
        else:
            tool_path = module_or_path

        # Extra important detail, need time last modified
        tool_data['last_modified'] = os.path.getmtime(tool_path)

        # Add to output
        tools_dict[tool_path] = tool_data

    # Simply dump dictionary to .json file now
    with open(TOOLS_INDEX_PATH, 'w') as fd:
        json.dump(tools_dict, fd, indent=2)


# Get tool scripts as absolute, case-normalized paths
def get_tool_scripts() -> list[str]:
    files = os.listdir(TOOLS_PATH)

    python_files = [f for f in files if f.endswith('.py') and f != '__init__.py']
    if not python_files:
        logging.warning("No Python scripts found in 'tools' folder.")
        return []

    python_files = sorted(python_files)

    # Convert to absolute paths and return
    return [os.path.normcase(os.path.join(TOOLS_PATH, filename)) for filename in python_files]


def get_indexed_tools() -> PartialToolListType | None:
    try:
        with open(TOOLS_INDEX_PATH, 'r') as fd:
            tools_index = json.load(fd)
    except (OSError, json.JSONDecodeError):
        logging.debug('Failed to load tools index... Will regenerate')
        return None

    output_tools = []
    for tool_path, meta_dict in tools_index.items():
        # Normalize tool_path for Windows
        tool_path = os.path.normcase(tool_path)

        # First check if tool_path exists and is file...
        if not os.path.isfile(tool_path):
            continue

        # Check modify time
        index_mtime = meta_dict['last_modified']
        actual_mtime = os.path.getmtime(tool_path)

        # If the file has been changed, reload the tool script...
        if index_mtime != actual_mtime:
            tool_tuple = load_tool(tool_path)
            if tool_tuple is None:
                print(f'Failed to load tool from index: {tool_path}')
                continue

            output_tools.append(tool_tuple)
        else:
            output_tools.append((tool_path, ToolMetadata.from_dict(meta_dict)))

    # Process any added tools
    for script_path in get_tool_scripts():
        # If tool not found in index, load and add it
        if script_path not in tools_index:
            tool_tuple = load_tool(script_path)
            if tool_tuple is None:
                print(f'Failed to load tool: {script_path}')
                continue

            output_tools.append(tool_tuple)

    # Sort tools alphabetically by tool name
    output_tools.sort(key=lambda tool_tuple: tool_tuple[-1].tool_name)
    return output_tools


def load_tools(verbose=True) -> PartialToolListType:
    # First load the index
    logging.debug('Loading index file...')
    tools_index = get_indexed_tools()

    # If we were successful in loading the tools index, perfect we're done!
    if tools_index:
        make_tools_index(tools_index)
        return tools_index

    # Get all tooling scripts
    if not os.path.exists(TOOLS_PATH):
        os.mkdir(TOOLS_PATH)

    tool_paths = get_tool_scripts()

    # Append each successfully loaded tool to the output
    tools = []
    for path in tool_paths:
        load_result = load_tool(path, verbose=verbose)
        if load_result is None:
            continue
        tools.append(load_result)

    # Create index for future execution
    make_tools_index(tools)

    return tools


class PyTowerParser(argparse.ArgumentParser):
    def error(self, message):
        if 'the following arguments are required' in message:
            self.print_help(sys.stderr)
            self.exit(2, f'\n{message.capitalize()}\n')
        else:
            super().error(message)

    def add_subparsers(self, **kwargs):
        kwargs['parser_class'] = PyTowerParser
        return super().add_subparsers(**kwargs)


def get_parser(tool_names: str):
    parser = PyTowerParser(prog='pytower',
                           description='High-level toolset and Python API for Tower Unite map editing',
                           epilog=f'Detected tools: {tool_names}')

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest='subcmd')

    # Help subcommand
    subparsers.add_parser('help', help='%(prog)s help')

    # Version subcommand
    subparsers.add_parser('version', help='%(prog)s version')

    # Convert subcommand
    convert_parser = subparsers.add_parser('convert', help='Convert given file to .json or CondoData')
    convert_parser.add_argument('filename', type=str, help='File to use as input')

    # List subcommand
    subparsers.add_parser('list', help='List tools')

    # Info subcommand
    info_parser = subparsers.add_parser('info', help='More information about tool')
    info_parser.add_argument('tool', type=str, help='Tool to get information about')

    # Run subcommand
    run_parser = subparsers.add_parser('run', help='Run given tool')

    # Required tool parameter
    run_parser.add_argument('tool', type=str, help='Tool to use')

    # Run parameters
    run_parser.add_argument('-i', '--input', dest='input', type=str, default='CondoData',
                            help='Input file')
    run_parser.add_argument('-o', '--output', dest='output', type=str, default='CondoData_output',
                            help='Output file')
    run_parser.add_argument('-s', '--select', dest='selection', type=str, default='items',
                            help='Selection type')

    # Flags
    run_parser.add_argument('-v', '--invert', dest='invert', action='store_true',
                            help='Whether or not to invert selection')
    run_parser.add_argument('-vf', '--invert-full', dest='invert-full', action='store_true',
                            help='Whether or not to do a full inversion (included property-only objects)')
    run_parser.add_argument('-j', '--json', dest='json', type=bool, action=argparse.BooleanOptionalAction,
                            help='Whether to load/save as .json, instead of converting to CondoData')
    run_parser.add_argument('-@', '--params', '--parameters', dest='parameters', nargs='*',
                            help='Parameters to pass onto tooling script (must come at end)')

    return parser


def parse_args(parser=None):
    if parser is None:
        parser = get_parser('')

    return vars(parser.parse_args())


def parse_selection(select_input: str) -> Selector:
    select_input = select_input.strip().casefold()
    if select_input == 'all' or select_input == 'everything':
        return ItemSelector()


def parse_parameters(param_input: list[str], meta: ToolMetadata) -> ParameterDict:
    # Ensure that all inputs were parsed correctly as strings
    params = {}
    for param in param_input:
        if not isinstance(param, str):
            logging.error(f'Invalid parameter: {param}.\n\nShould have format "parameter=value" with no spaces.')
            sys.exit(1)

        param_split = param.split('=')
        if len(param_split) != 2:
            logging.error(f'Invalid parameter: {param}.\n\nShould have format "parameter=value" with no spaces and only'
                          f'one equal sign.')
            sys.exit(1)

        param_name, value = param_split
        param_name = param_name.strip().casefold()
        if param_name in meta.params:
            # Typecast value to expected type
            value = meta.params[param_name].dtype(value)

        params[param_name] = value

    # Make the user input any other required parameters
    for param, info in meta.params.items():
        if param in params:
            continue

        # If parameter has a default use that, making it optional
        if info.default is not None:
            params[param] = info.default
            continue

        # Load in non-optional parameter: prompt user for input
        value = input(f'Enter value for {param.lower()}: ')
        try:
            value = info.dtype(value)
        except Exception as e:
            print(f'Invalid value for {param.lower()}: {e}')
            sys.exit(1)
        params[param] = value

    # Add support for accessing parameters using dot notation by constructing ParameterDict
    params = ParameterDict(params)
    return params


def load_suitebro(filename: str, only_json=False) -> Suitebro:
    abs_filepath = os.path.realpath(filename)
    in_dir = os.path.dirname(abs_filepath)
    json_output_path = os.path.join(in_dir, os.path.basename(abs_filepath) + ".json")

    if not only_json:
        run_suitebro_parser(abs_filepath, False, json_output_path, overwrite=True)

    logging.info('Loading JSON file...')
    with open(json_output_path, 'r') as fd:
        save_json = json.load(fd)

    save = Suitebro(save_json)
    _active_saves.append(save)

    return save


def save_suitebro(save: Suitebro, filename: str, only_json=False):
    abs_filepath = os.path.realpath(filename)
    out_dir = os.path.dirname(abs_filepath)
    json_final_path = os.path.join(out_dir, f'{filename}.json')
    final_output_path = os.path.join(out_dir, f'{filename}')

    with open(json_final_path, 'w') as fd:
        json.dump(save.to_dict(), fd, indent=2)

    # Finally run!
    if not only_json:
        run_suitebro_parser(json_final_path, True, final_output_path, overwrite=True)

    # Remove from active saves
    _active_saves.remove(save)


def run(input_filename: str, tool: ToolMainType, selector: Selector = None, params: list = []):
    tool_path = tool.__globals__['__file__']
    mock_tool, mock_metadata = load_tool(tool_path)
    mock_params = parse_parameters(params, mock_metadata)

    save = load_suitebro(input_filename)

    logging.info(f'Running {mock_metadata.tool_name} with parameters {mock_params}')

    if selector is None:
        selector = ItemSelector()

    tool(save, selector.select(Selection(save.objects)), mock_params)

    save_suitebro(save, f'{input_filename}_output')


# Returns tool if could find tool disambiguated, otherwise returns None
def find_tool(tools: PartialToolListType, name: str) -> tuple[ModuleType | str, ToolMetadata] | None:
    max_prefix_len = 0
    best_match = None
    conflict = False

    name = name.casefold().strip()
    for module_or_path, meta in tools:
        tool_name = meta.tool_name.casefold().strip()
        # Use os.path.commonprefix as a utility I guess
        prefix = os.path.commonprefix([name, tool_name])
        prefix_len = len(prefix)
        if prefix_len == max_prefix_len:
            conflict = True
        elif prefix_len > max_prefix_len:
            conflict = False
            max_prefix_len = prefix_len
            best_match = module_or_path, meta

    if best_match is None or conflict:
        return None

    return best_match


def main():
    tools = load_tools(verbose=True)
    tool_names = ', '.join([meta.tool_name for _, meta in tools])
    parser = get_parser(tool_names)
    args = parse_args(parser)

    if not args['subcmd']:
        parser.print_help(sys.stdout)
        sys.exit(0)

    match args['subcmd']:
        case 'help':
            parser.print_help(sys.stdout)
            sys.exit(0)
        case 'version':
            print(f'PyTower {__version__}')
            sys.exit(0)
        case 'convert':
            filename = args['filename'].strip()
            abs_filepath = os.path.realpath(filename)
            in_dir = os.path.dirname(abs_filepath)

            if filename.endswith('.json'):
                output = os.path.join(in_dir, filename[:-5])
                run_suitebro_parser(abs_filepath, True, output, overwrite=True)
            else:
                output = os.path.join(in_dir, os.path.basename(abs_filepath) + '.json')
                run_suitebro_parser(abs_filepath, False, output, overwrite=True)
            sys.exit(0)
        case 'list':
            print('Available tools:')
            for _, meta in tools:
                tool_str = f'  {meta.tool_name}'
                if meta.version is not None:
                    tool_str += f' (v{meta.version})'
                if meta.author is not None:
                    tool_str += f' by {meta.author}'
                print(tool_str)
            sys.exit(0)
        case 'info':
            tool_name = args['tool'].strip().casefold()
            tool = find_tool(tools, tool_name)
            if tool:
                _, meta = tool
                print(meta.get_info())
                sys.exit(0)

            logging.error(f'Could not find {args["tool"]}! \n\nAvailable tools: {tool_names}')
            sys.exit(1)
        case 'run':
            # Parse tool name
            tool_name = args['tool'].strip().casefold()
            tool = find_tool(tools, tool_name)

            # Error if could not find specified tool
            if not tool:
                logging.error(f'Could not find {args["tool"]}! \n\nAvailable tools: {tool_names}')
                sys.exit(1)

            module_or_path, meta = tool
            if not isinstance(module_or_path, ModuleType):
                module, _ = load_tool(module_or_path)
            else:
                module = module_or_path

            # TODO lookahead for overwrite to detect issues and error out before even starting

            # Input file name
            input_filename = args['input']

            # Whether or not to only use json
            only_json = not args['json']
            if only_json:
                # Remove .json to be consistent with rest of program
                if input_filename.endswith('.json'):
                    input_filename = input_filename[:-5]

            # Load save
            save = load_suitebro(input_filename, only_json=only_json)

            # Default selector is ItemSelector
            selector = ItemSelector()

            # If --select argument provided, choose different selector
            if 'selection' in args:
                sel_input: str = args['selection'].casefold().strip()
                sel_split = sel_input.split(':')

                bad_sel = False
                if len(sel_split) > 2:
                    bad_sel = True
                elif sel_input == 'item' or sel_input == 'items':
                    selector = ItemSelector()
                elif sel_input == 'all' or sel_input == 'everything':
                    selector = EverythingSelector()
                elif sel_input == 'none' or sel_input == 'nothing':
                    selector = NothingSelector()
                elif sel_input.startswith('group:'):
                    gid_input = sel_split[1]
                    try:
                        group_id = int(gid_input)
                        selector = GroupSelector(group_id)
                    except ValueError:
                        print(f'{gid_input} is not valid group_id!')
                        bad_sel = True
                elif sel_input.startswith('regex:'):
                    selector = RegexSelector(sel_split[1])
                elif sel_input.startswith('name:'):
                    selector = NameSelector(sel_split[1])
                elif sel_input.startswith('customname:'):
                    selector = CustomNameSelector(sel_split[1])
                elif sel_input.startswith('objname:'):
                    selector = CustomNameSelector(sel_split[1])
                else:
                    bad_sel = True

                if bad_sel:
                    print(f'Invalid selection: {sel_input}')
                    print('\nAvailable selection options: name:<NAME>, customname:<NAME>, objname:<NAME>, group:<ID>,'
                          ' items, all, none, regex:<PATTERN>')
                    print('\nExample usages:\n  --select group:4\n  --select name:FrontDoor\n  --select regex:Canvas.*')
                    sys.exit(1)

            selection = selector.select(Selection(save.objects))

            if args['invert-full'] and args['invert']:
                print('--invert-all and --invert cannot be used at the same time!')
                sys.exit(1)

            if args['invert-full']:
                selection = Selection(save.objects) - selection
            if args['invert']:
                selection = ItemSelector().select(Selection(save.objects)) - selection

            # Run tool
            params = parse_parameters(args['parameters'], meta)
            logging.info(f'Running {meta.tool_name} with parameters {params}')
            module.main(save, selection, params)

            # Writeback save
            save_suitebro(save, args['output'], only_json=only_json)

if __name__ == '__main__':
    main()
