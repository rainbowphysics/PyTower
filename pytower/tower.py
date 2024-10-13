import argparse
import os
import sys
from types import ModuleType
from typing import Any, cast

import colorama
from colorama import Fore, Style

from .__config__ import __version__
from .backup import make_backup, restore_backup, fix_canvases
from .config import TowerConfig
from .image_backends.backend import ResourceBackend
from .image_backends.custom import CustomBackend
from .image_backends.catbox import CatboxBackend
from .image_backends.imgur import ImgurBackend
from .logging import *
from .selection import *
from .suitebro import load_suitebro, save_suitebro, run_suitebro_parser
from .tool_lib import ToolMetadata, ParameterDict, ToolMainType, load_tool, PartialToolListType, load_tools, \
    make_tools_index
from .util import not_none, xyz


class PyTowerParser(argparse.ArgumentParser):
    def error(self, message: str):
        if 'the following arguments are required' in message:
            self.print_help(sys.stderr)
            self.exit(2, f'\n{message.capitalize()}\n')
        else:
            super().error(message)

    def add_subparsers(self, **kwargs):
        kwargs['parser_class'] = PyTowerParser
        return super().add_subparsers(**kwargs)


def get_parser(tool_names: str) -> PyTowerParser:
    """
    Args:
        tool_names: List of tool names as a string. Used when running `pytower`

    Returns:
        The argparse parser used to parse the program input
    """
    parser = PyTowerParser(prog='pytower',
                           description='High-level toolset and Python API for Tower Unite map editing',
                           epilog=f'Detected tools: {tool_names}')

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest='subcmd')

    # Help subcommand
    subparsers.add_parser('help', help='PyTower help')

    # Version subcommand
    subparsers.add_parser('version', help='PyTower version')

    # Convert subcommand
    convert_parser = subparsers.add_parser('convert', help='Convert given file to .json or CondoData')
    convert_parser.add_argument('filename', type=str, help='File to use as input')

    # Backup subcommand
    backup_parser = subparsers.add_parser('backup', help='Backup or restore canvases for save files')
    backup_parser.add_argument('mode', type=str, help='Mode to use (save or restore)')
    backup_parser.add_argument('filename', type=str, help='Name of file to use')
    backup_parser.add_argument('-f', '--force', dest='force', type=bool, action=argparse.BooleanOptionalAction,
                               help='Whether to force reupload on restore or not')
    backup_parser.add_argument('-b', '--backend', dest='backend', type=str, default='catbox',
                               help='Backend to use (Imgur or Catbox)')

    # List subcommand
    subparsers.add_parser('list', help='List tools')

    # Info subcommand
    info_parser = subparsers.add_parser('info', help='More information about tool')
    info_parser.add_argument('tool', type=str, help='Tool to get information about')

    # Scan subcommand
    scan_parser = subparsers.add_parser('scan', help='Scan given directory for tools')
    scan_parser.add_argument('path', type=str, help='Path to use (use "." for current directory)')

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
                            help='Whether to invert selection')
    run_parser.add_argument('-vf', '--invert-full', dest='invert-full', action='store_true',
                            help='Whether to do a full inversion (included property-only objects)')
    run_parser.add_argument('-j', '--json', dest='json', type=bool, action=argparse.BooleanOptionalAction,
                            help='Whether to load/save as .json, instead of converting to CondoData')
    run_parser.add_argument('-g', '--groups', '--per-group', dest='per_group', action='store_true',
                            help='Whether to apply the tool per group')
    run_parser.add_argument('-r', '--num-runs', '--num-times', dest='num_runs', type=int, default=1,
                            help='Number of times to run tool')
    run_parser.add_argument('-@', '--params', '--parameters', dest='parameters', nargs='*', default=[],
                            help='Parameters to pass onto tooling script (must come at end)')

    # Fix subcommand
    fix_parser = subparsers.add_parser('fix', help='Fix broken canvases and corruption in given file')
    fix_parser.add_argument('filename', type=str, help='File to use as input')
    fix_parser.add_argument('-f', '--force', dest='force', type=bool, action=argparse.BooleanOptionalAction,
                            help='Whether to force reupload of all canvases or not')
    fix_parser.add_argument('-b', '--backend', dest='backend', type=str, default='catbox',
                            help='Backend to use (Imgur or Catbox)')

    # Compress subcommand
    compress_parser = subparsers.add_parser('compress', help='Compress file by removing some default fields')
    compress_parser.add_argument('filename', type=str, help='File to use as input')

    # Config subcommand
    config_parser = subparsers.add_parser('config', help='PyTower configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_mode', required=True)
    config_get_parser = config_subparsers.add_parser('get', help='Get value in config')
    config_get_parser.add_argument('key', type=str, help='Key to get in config')
    config_set_parser = config_subparsers.add_parser('set', help='Set value in config')
    config_set_parser.add_argument('key', type=str, help='Key to set in config')
    config_set_parser.add_argument('value', type=str, help='Value to set within config', nargs='*')
    config_view_parser = config_subparsers.add_parser('view', help='View config')

    return parser


def parse_args(parser: PyTowerParser | None = None):
    if parser is None:
        parser = get_parser('')

    return vars(parser.parse_args())


def parse_parameters(param_input: list[Any], meta: ToolMetadata) -> ParameterDict:
    """
    Parse input parameters into a ParameterDict to pass into tool's main method

    Args:
        param_input: List of strings in the format "parameter=value" to be parsed
        meta: Accompanying metadata of the tool being run

    Returns:
        ParameterDict object containing parsed parameters, which can be accessed with dot notation or like a dictionary
    """
    # Ensure that all inputs were parsed correctly as strings
    params = {}
    for param in param_input:
        if not isinstance(param, str):
            error(f'Invalid parameter: {param}.\n\nShould have format "parameter=value" with no spaces.')
            sys.exit(1)

        param_split = param.split('=')
        if len(param_split) != 2:
            error(f'Invalid parameter: {param}.\n\nShould have format "parameter=value" with no spaces and only'
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
            error(f'Invalid value for {param.lower()}: {e}')
            sys.exit(1)
        params[param] = value

    # Add support for accessing parameters using dot notation by constructing ParameterDict
    params = ParameterDict(params)
    return params


def run(input_filename: str, tool: ToolMainType, selector: Selector | None = None, params: list[str] | None = None):
    """
    Mock run for rapid prototyping tools

    Args:
        input_filename: Path or filename of the CondoData/.map file to use
        tool: Main method reference for the tool to run
        selector: Selector to use on input
        params: Parameter list
    """
    if params is None:
        params = []
    tool_path: str = tool.__globals__['__file__']
    mock_tool, mock_metadata = not_none(load_tool(tool_path))
    mock_params = parse_parameters(params, mock_metadata)

    save = load_suitebro(input_filename)

    info(f'Running tool {mock_metadata.tool_name}...')

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
        if meta.hidden:
            continue

        tool_name = meta.tool_name.casefold().strip()

        # Handles aliased/duplicated tool names
        if name == tool_name:
            best_match = module_or_path, meta
            conflict = False
            break

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


def get_tool_names(tools: PartialToolListType) -> str:
    return ', '.join([meta.tool_name for _, meta in tools if not meta.hidden])


def config_confirm_show() -> bool:
    warning('This config command may display personal information. Are you sure you want to continue?')
    response = input('Y/n? >')
    if 'yes'.startswith(response.strip().casefold()):
        return True

    return False


def parse_selector(selection_input: str) -> Selector | None:
    """
    Parses a single selector string input into a Selector object

    Args:
        selection_input: Input string to parse

    Returns:
        Parsed Selector object
    """
    sel_input = selection_input.casefold().strip()
    sel_split = sel_input.split(':')
    sel_split_case_sensitive = selection_input.strip().split(':')

    if len(sel_split) > 2:
        return None
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
            error(f'{gid_input} is not valid group_id!')
            return None
    elif sel_input.startswith('regex:'):
        selector = RegexSelector(sel_split_case_sensitive[1])
    elif sel_input.startswith('name:'):
        selector = NameSelector(sel_split[1])
    elif sel_input.startswith('customname:'):
        selector = CustomNameSelector(sel_split[1])
    elif sel_input.startswith('objname:'):
        selector = ObjectNameSelector(sel_split[1])
    elif sel_input.startswith('random:'):
        probability = float(sel_split[1])
        selector = RandomSelector(probability)
    elif sel_input.startswith('take:') or re.match('\\d+', sel_input):
        try:
            num = int(sel_split[1])
        except IndexError:
            num = int(sel_input)
        selector = TakeSelector(num)
    elif re.match('\\d+\\.*\\d*%', sel_input):
        percentage = float(sel_split[1][:-1])
        selector = PercentSelector(percentage)
    elif sel_input.startswith('box:'):
        positions = sel_split[1].split('/')
        pos1 = xyz(positions[0])
        pos2 = xyz(positions[1])
        selector = BoxSelector(pos1, pos2)
    elif sel_input.startswith('sphere:'):
        params = sel_split[1].split('/')
        center = xyz(params[0])
        radius = float(params[1])
        selector = SphereSelector(center, radius)
    else:
        return None

    return selector


def parse_selectors(selection_input: str) -> list[Selector]:
    """
    Parses an input string, where each selector is separated with a ';', into a sequence of Selector objects

    Args:
        selection_input: String input to parse

    Returns:
        List of Selector
    """
    inputs = selection_input.split(';')
    selectors = [parse_selector(input_sel) for input_sel in inputs]

    # Validate
    for selector, sel_input in zip(selectors, inputs):
        if not selector:
            error(f'Invalid selection: {sel_input}')
            info('\nExample usages:\n  --select group:4\n  --select name:FrontDoor\n  --select regex:Canvas.*')
            sys.exit(1)

    return cast(list[Selector], selectors)  # We know it's not None!


def get_resource_backends() -> list[ResourceBackend]:
    """
    Returns:
        List of ResourceBackends registered with PyTower
    """
    from pytower.config import CONFIG, KEY_IMGUR_CLIENT_ID, KEY_CATBOX_USERHASH
    imgur_client_id = CONFIG.get(KEY_IMGUR_CLIENT_ID, str)
    user_hash = CONFIG.get(KEY_CATBOX_USERHASH, str)
    return [ImgurBackend(imgur_client_id), CatboxBackend(user_hash), CustomBackend()]


def parse_resource_backend(backends: list[ResourceBackend], backend_input: str) -> ResourceBackend:
    sanitized = backend_input.strip().casefold()
    for backend in backends:
        if backend.name.strip().casefold().startswith(sanitized):
            return backend

    error(f'Invalid backend {backend_input}!'
          f' Available backends: {", ".join([backend.name for backend in backends])}')
    sys.exit(1)


def version() -> str:
    """
    PyTower version

    Returns:
        The version as a string, in the format "PyTower {version}"
    """
    return f'PyTower {__version__}'


def convert(filename: str):
    """
    Converts input into .json or vice versa, from the uesave tower-unite-suitebro .json format

    Args:
        filename: Path or file name of the CondoData/.map file to convert
    """
    filename = filename.strip()
    abs_filepath = os.path.realpath(filename)
    in_dir = os.path.dirname(abs_filepath)

    if filename.endswith('.json'):
        output = os.path.join(in_dir, filename[:-5])
        run_suitebro_parser(abs_filepath, True, output, overwrite=True)
    else:
        output = os.path.join(in_dir, os.path.basename(abs_filepath) + '.json')
        run_suitebro_parser(abs_filepath, False, output, overwrite=True)


def backup(mode: str, filename: str, backends: list[ResourceBackend] | None = None, backend: str = 'Catbox',
           force: bool = False):
    """
    Prints list of tools

    Args:
        mode: Either 'save' or 'restore'
        filename: Path or file name of the CondoData/.map file to backup
        backends: List of resource backends, if included avoids reloading
        backend: Backend to use when restoring
        force: Whether to force reupload of resources
    """
    if backends is None:
        backends = get_resource_backends()

    match mode:
        case 'save':
            if not os.path.isfile(filename):
                error(f'Could not find {filename}!')
                sys.exit(1)

            save = load_suitebro(filename)
            make_backup(save)
        case 'restore':
            from .backup import BACKUP_DIR
            path = os.path.join(BACKUP_DIR, filename)
            if not os.path.isdir(path):
                error(f'Could not find backup {path}!'
                      f' Input must be the name of a folder in backups directory')
                sys.exit(1)

            backend = parse_resource_backend(backends, backend)

            restore_backup(path, force_reupload=force, backend=backend)
        case _:
            pass


def list_tools(tools: PartialToolListType | None = None):
    """
    Prints list of tools

    Args:
        tools: List of tools, if included avoids reloading the tool index
    """
    if tools is None:
        tools = load_tools()

    info('Available tools:')
    for _, meta in tools:
        if meta.hidden:
            continue

        tool_str = f'  {meta.tool_name}'
        if meta.version is not None:
            tool_str += f' (v{meta.version})'
        if meta.author is not None:
            tool_str += f' by {meta.author}'
        info(tool_str)


def info_tool(tool_input: str, tools: PartialToolListType | None = None, tool_names: str = ''):
    """
    Prints information about input tool name

    Args:
        tool_input: Name of the tool to print info for
        tools: List of tools, if included avoids reloading the tool index
        tool_names: Tool names, if included avoids recalculating
    """
    if tools is None:
        tools = load_tools()

    tool_name = tool_input.strip().casefold()
    tool = find_tool(tools, tool_name)
    if tool:
        _, meta = tool
        info(meta.get_info())
        return

    error(f'Could not find {tool_input}! \n')

    if not tool_names:
        tool_names = get_tool_names(tools)
    info(f'Available tools: {tool_names}')

    sys.exit(1)


def scan(path: str, tools: PartialToolListType | None = None) -> PartialToolListType:
    """
    Scans a directory for tool scripts and registers detected tool scripts

    Args:
        path: Path of directory to scan
        tools: List of tools, if included avoids reloading the tool index
    """
    if tools is None:
        tools = load_tools()

    for file in os.listdir(path):
        if file.endswith('.py') and file != '__init__.py' and file != '__main__.py' and file != 'setup.py':
            abs_path = os.path.normcase(os.path.abspath(file))

            # Check if files already exist before registering them
            exists = False
            for tool_tuple in tools:
                module_or_path, _ = tool_tuple
                if isinstance(module_or_path, ModuleType):
                    path = os.path.normcase(module_or_path.__file__)
                else:
                    path = module_or_path

                if abs_path == path:
                    exists = True
                    break

            if exists:
                info(f'Found already registered script {file}')
                continue

            # At this point, the tool script must be novel so load it
            tool_tuple = load_tool(file)
            if tool_tuple is not None:
                tools.append(tool_tuple)

    # Finally update tools index
    make_tools_index(tools)
    return tools


def fix(filename: str, backends: list[ResourceBackend] | None = None, backend: str = 'Catbox', force: bool = False):
    """
    Scans a directory for tool scripts and registers detected tool scripts

    Args:
        filename: Path or file name of the CondoData/.map file to fix
        backends: List of resource backends, if included avoids reloading
        backend: Backend to use when fixing
        force: Whether to force reupload of resources
    """
    if backends is None:
        backends = get_resource_backends()

    filename = filename.strip()
    path = os.path.abspath(os.path.expanduser(filename))
    backend = parse_resource_backend(backends, backend)
    fix_canvases(path, force_reupload=force, backend=backend)


def main():
    """Entrypoint for PyTower"""
    debug(f"Ran command {' '.join(sys.argv)}")

    # Initialize colorama for pretty printing
    colorama.init(convert=sys.platform == 'win32')

    config = TowerConfig('config.json')

    tools = load_tools()
    tool_names = get_tool_names(tools)
    parser = get_parser(tool_names)
    args = parse_args(parser)

    backends = get_resource_backends()

    if not args['subcmd']:
        parser.print_help(sys.stdout)
        sys.exit(0)

    match args['subcmd']:
        case 'help':
            parser.print_help(sys.stdout)
        case 'version':
            info(version())
        case 'convert':
            convert(args['filename'])
        case 'backup':
            backup(args['mode'], args['filename'], backends, args['backend'], args['force'])
        case 'list':
            list_tools(tools)
        case 'info':
            info_tool(args['tool'], tools, tool_names)
        case 'scan':
            scan(args['path'], tools)
        case 'run':
            # Parse tool name
            tool_name = args['tool'].strip().casefold()
            tool = find_tool(tools, tool_name)

            # Error if could not find specified tool
            if not tool:
                error(f'Could not find {args["tool"]}! \n\nAvailable tools: {tool_names}')
                sys.exit(1)

            module_or_path, meta = tool
            if not isinstance(module_or_path, ModuleType):
                module, _ = load_tool(module_or_path)
            else:
                module = module_or_path

            # Input file name
            input_filename = args['input']

            # Whether to only use json
            only_json = args['json']
            if only_json:
                # Remove .json to be consistent with rest of program
                if input_filename.endswith('.json'):
                    input_filename = input_filename[:-5]

            # Load save
            save = load_suitebro(input_filename, only_json=only_json)

            inv_items_count = save.inventory_count()

            # If --select argument provided, choose different selector
            if args['selection']:
                selectors = parse_selectors(args['selection'])
            else:
                selectors = [ItemSelector()]

            selection = Selection(save.objects)
            for selector in selectors:
                selection = selector.select(selection)

            if args['invert-full'] and args['invert']:
                critical('--invert-all and --invert cannot be used at the same time!')
                sys.exit(1)

            if args['invert-full']:
                selection = Selection(save.objects) - selection
            if args['invert']:
                selection = ItemSelector().select(Selection(save.objects)) - selection

            # Run tool
            params = parse_parameters(args['parameters'], meta)
            num_runs: int = args['num_runs']
            if num_runs == 1:
                info(f'Running tool {meta.tool_name}...')
            elif num_runs > 1:
                info(f'Running tool {meta.tool_name} {num_runs} times...')

            for _ in range(num_runs):
                if not args['per_group']:
                    # Normal execution
                    module.main(save, selection, params)
                else:
                    # Per group execution
                    for (group_id, group) in selection.groups():
                        module.main(save, group, params)

                    # Ungrouped items are treated as being in a group by themselves
                    for obj in selection.ungrouped():
                        module.main(save, Selection({obj}), params)

            # Skip writeback if tool has NO_WRITE = True
            if meta.nowrite:
                return

            # Writeback save
            save_suitebro(save, args['output'], only_json=only_json)
            success(f'Exported to {args["output"]}!')

            # Display items in save
            final_inv_items_count = save.inventory_count()
            print_items = False
            for name, count in final_inv_items_count.items():
                if name not in inv_items_count or final_inv_items_count[name] > inv_items_count[name]:
                    print_items = True
                    break

            if print_items:
                info('Make sure you have the following items in your inventory before loading the map:')
                for name, count in final_inv_items_count.items():
                    info(f'{count:>9,}x {name}')
        case 'fix':
            fix(args['filename'], backends, args['backend'], args['force'])
        case 'compress':
            filename = args['filename']
            if not os.path.isfile(filename):
                error(f'Could not find {filename}!')
                sys.exit(1)

            save = load_suitebro(filename)
            for obj in save.objects:
                obj.compress()

            save_suitebro(save, filename)
        case 'config':
            match args['config_mode']:
                case 'get':
                    if config_confirm_show():
                        info(config.get(args['key']))
                case 'set':
                    k, v = args['key'], ' '.join(args['value'])
                    try:
                        if v.strip().casefold() in ['true', 'false']:
                            config.set(k, bool(v))
                        else:
                            config.set(k, v)
                        success(f'{k} is now set to {v}')
                    except ValueError:
                        error(f'{k} is not in config!')
                        info(f'List of config keys: {"".join(config.keys())}')
                case 'view':
                    if config_confirm_show():
                        for k, v in dict(config).items():
                            info(f'{k}: {v}')
                case _:
                    pass
        case _:
            pass


if __name__ == '__main__':
    main()
