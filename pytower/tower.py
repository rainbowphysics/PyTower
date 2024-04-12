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

import colorama
import numpy as np
import platform

from colorama import Fore, Back, Style

from pytower.image_backends.catbox import CatboxBackend
from pytower.image_backends.imgur import ImgurBackend
from . import __version__, root_directory, backup
from .backup import make_backup
from .config import TowerConfig
from .selection import *
from .suitebro import Suitebro, load_suitebro, save_suitebro, run_suitebro_parser
from .tool_lib import ToolMetadata, ParameterDict, ToolMainType, load_tool, PartialToolListType, load_tools, \
    make_tools_index
from .util import xyz, xyzint, xyz_to_string


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

    # Backup subcommand
    backup_parser = subparsers.add_parser('backup', help='Backup or restore canvases for save files')
    backup_parser.add_argument('mode', type=str, help='Mode to use (save or restore)')
    backup_parser.add_argument('filename', type=str, help='Name of file to use')

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
                            help='Whether or not to invert selection')
    run_parser.add_argument('-vf', '--invert-full', dest='invert-full', action='store_true',
                            help='Whether or not to do a full inversion (included property-only objects)')
    run_parser.add_argument('-j', '--json', dest='json', type=bool, action=argparse.BooleanOptionalAction,
                            help='Whether to load/save as .json, instead of converting to CondoData')
    run_parser.add_argument('-g', '--groups', '--per-group', dest='per_group', action='store_true',
                            help='Whether or not to apply the tool per group')
    run_parser.add_argument('-@', '--params', '--parameters', dest='parameters', nargs='*', default={},
                            help='Parameters to pass onto tooling script (must come at end)')

    # Fix subcommand
    fix_parser = subparsers.add_parser('fix', help='Fix broken canvases and corruption in given file')
    fix_parser.add_argument('filename', type=str, help='File to use as input')
    fix_parser.add_argument('-f', '--force', dest='force', type=bool, action=argparse.BooleanOptionalAction,
                            help='Whether to force reupload of all canvases or not')
    fix_parser.add_argument('-b', '--backend', dest='backend', type=str,
                            help='Backend to use (Imgur or Catbox)')

    # Config subcommand
    config_parser = subparsers.add_parser('config', help='PyTower Configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_mode', required=True)
    config_get_parser = config_subparsers.add_parser('get', help='Get value in config')
    config_get_parser.add_argument('key', type=str, help='Key to get in config')
    config_set_parser = config_subparsers.add_parser('set', help='Set value in config')
    config_set_parser.add_argument('key', type=str, help='Key to set in config')
    config_set_parser.add_argument('value', type=str, help='Value to set within config')
    config_view_parser = config_subparsers.add_parser('view', help='View config')

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


def main():
    # Initialize colorama for pretty printing
    colorama.init(convert=sys.platform == 'win32')

    config = TowerConfig('config.json')

    tools = load_tools(verbose=True)
    tool_names = ', '.join([meta.tool_name for _, meta in tools if not meta.hidden])
    parser = get_parser(tool_names)
    args = parse_args(parser)

    if not args['subcmd']:
        parser.print_help(sys.stdout)
        sys.exit(0)

    match args['subcmd']:
        case 'help':
            parser.print_help(sys.stdout)
        case 'version':
            print(f'PyTower {__version__}')
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
        case 'backup':
            match args['mode']:
                case 'save':
                    filename = args['filename']
                    if not os.path.isfile(filename):
                        print(f'Could not find {filename}!')
                        sys.exit(1)

                    save = load_suitebro(filename)
                    make_backup(save)
                case 'restore':
                    pass
        case 'list':
            print('Available tools:')
            for _, meta in tools:
                if meta.hidden:
                    continue

                tool_str = f'  {meta.tool_name}'
                if meta.version is not None:
                    tool_str += f' (v{meta.version})'
                if meta.author is not None:
                    tool_str += f' by {meta.author}'
                print(tool_str)
        case 'info':
            tool_name = args['tool'].strip().casefold()
            tool = find_tool(tools, tool_name)
            if tool:
                _, meta = tool
                print(meta.get_info())
                sys.exit(0)

            logging.error(f'Could not find {args["tool"]}! \n\nAvailable tools: {tool_names}')
            sys.exit(1)
        case 'scan':
            for file in os.listdir(args['path']):
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
                        print(f'Found already registered script {file}')
                        continue

                    # At this point, the tool script must be novel so load it
                    tool_tuple = load_tool(file)
                    if tool_tuple is not None:
                        tools.append(tool_tuple)

            # Finally update tools index
            make_tools_index(tools)
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

            # Input file name
            input_filename = args['input']

            # Whether or not to only use json
            only_json = args['json']
            if only_json:
                # Remove .json to be consistent with rest of program
                if input_filename.endswith('.json'):
                    input_filename = input_filename[:-5]

            # Load save
            save = load_suitebro(input_filename, only_json=only_json)

            inv_items = save.inventory_items()
            num_inv_items = len(inv_items)

            # Default selector is ItemSelector
            selector = ItemSelector()

            # If --select argument provided, choose different selector
            if 'selection' in args:
                sel_input: str = args['selection'].casefold().strip()
                sel_split = sel_input.split(':')
                sel_split_case_sensitive = args['selection'].strip().split(':')

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
                    selector = RegexSelector(sel_split_case_sensitive[1])
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

            # Writeback save
            save_suitebro(save, args['output'], only_json=only_json)

            print(Fore.GREEN + f'\nSuccessfully exported to {args["output"]}!')
            print(Style.RESET_ALL)

            # Display items in save
            final_inv_items = save.inventory_items()
            # TODO really this should check whether the quantity of a single item type has increased, but this is
            #  probably fine
            if len(final_inv_items) > num_inv_items:
                print('Make sure you have the following items in your inventory before loading the map:')
                final_inv_items = sorted(final_inv_items, key=TowerObject.get_name)
                for name, objs in itertools.groupby(final_inv_items, TowerObject.get_name):
                    quantity = len(list(objs))
                    print(f'{quantity:>9,}x {name}')
        case 'fix':
            filename = args['filename'].strip()
            path = os.path.abspath(os.path.expanduser(filename))
            if 'backend' in args:
                backend_input = args['backend'].strip().casefold()
                if 'imgur'.startswith(backend_input):
                    from pytower.config import CONFIG, KEY_IMGUR_CLIENT_ID
                    imgur_client_id = CONFIG.get(KEY_IMGUR_CLIENT_ID)
                    backend = ImgurBackend(imgur_client_id)
                elif 'catbox'.startswith(backend_input):
                    from pytower.config import CONFIG, KEY_CATBOX_USERHASH
                    user_hash = CONFIG.get(KEY_CATBOX_USERHASH)
                    backend = CatboxBackend(user_hash)
                else:
                    print(f'Invalid backend {args["backend"]}! Must be Imgur or Catbox', file=sys.stderr)
                    sys.exit(1)
            else:
                backend = CatboxBackend()  # default
            backup.fix_canvases(path, force_reupload=args['force'], backend=backend)
        case 'config':
            match args['config_mode']:
                case 'get':
                    print(config.get(args['key']))
                case 'set':
                    k, v = args['key'], args['value']
                    try:
                        if v.strip().casefold() in ['true', 'false']:
                            config.set(k, bool(v))
                        else:
                            config.set(k, v)
                    except ValueError:
                        print(f'{k} is not in config!')
                        print(f'List of config keys: {"".join(config.keys())}')
                    print(f'{k} is now set to {v}')
                case 'view':
                    for k, v in dict(config).items():
                        print(f'{k}: {v}')


if __name__ == '__main__':
    main()
