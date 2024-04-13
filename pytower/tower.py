import argparse
import logging
import os
import sys
from types import ModuleType

import colorama
from colorama import Fore, Style

from . import __version__, backup
from .backup import make_backup, restore_backup
from .config import TowerConfig
from .image_backends.backend import ResourceBackend
from .image_backends.catbox import CatboxBackend
from .image_backends.imgur import ImgurBackend
from .selection import *
from .suitebro import load_suitebro, save_suitebro, run_suitebro_parser
from .tool_lib import ToolMetadata, ParameterDict, ToolMainType, load_tool, PartialToolListType, load_tools, \
    make_tools_index
from .util import xyz


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
    backup_parser.add_argument('-f', '--force', dest='force', type=bool, action=argparse.BooleanOptionalAction,
                               help='Whether to force reupload on restore or not')

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
    run_parser.add_argument('-@', '--params', '--parameters', dest='parameters', nargs='*', default=[],
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
    config_set_parser.add_argument('value', type=str, help='Value to set within config', nargs='*')
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
            print(f'Invalid parameter: {param}.\n\nShould have format "parameter=value" with no spaces.', file=sys.stderr)
            sys.exit(1)

        param_split = param.split('=')
        if len(param_split) != 2:
            print(f'Invalid parameter: {param}.\n\nShould have format "parameter=value" with no spaces and only'
                          f'one equal sign.', file=sys.stderr)
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

    print(f'Running tool {mock_metadata.tool_name}...')

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


def config_confirm_show() -> bool:
    print('Warning, this config command may display personal information. Are you sure you want to continue?')
    response = input('Y/n? >')
    if 'yes'.startswith(response.strip().casefold()):
        return True

    return False


def parse_resource_backend(backend_input) -> ResourceBackend:
    sanitized = backend_input.strip().casefold()
    if 'imgur'.startswith(sanitized):
        from pytower.config import CONFIG, KEY_IMGUR_CLIENT_ID
        imgur_client_id = CONFIG.get(KEY_IMGUR_CLIENT_ID)
        return ImgurBackend(imgur_client_id)
    elif 'catbox'.startswith(sanitized):
        from pytower.config import CONFIG, KEY_CATBOX_USERHASH
        user_hash = CONFIG.get(KEY_CATBOX_USERHASH)
        return CatboxBackend(user_hash)
    else:
        print(f'Invalid backend {backend_input}! Must be Imgur or Catbox', file=sys.stderr)
        sys.exit(1)


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
                    filename = args['filename']
                    from .backup import BACKUP_DIR
                    path = os.path.join(BACKUP_DIR, filename)
                    if not os.path.isdir(path):
                        print(f'Could not find backup {path}!'
                              f' Input must be the name of a folder in backups dictory')
                        sys.exit(1)

                    if args['backend']:
                        backend = parse_resource_backend(args['backend'])
                    else:
                        backend = CatboxBackend()  # default

                    backup.restore_backup(path, force_reupload=args['force'], backend=backend)
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
                print(f'Could not find {args["tool"]}! \n\nAvailable tools: {tool_names}', file=sys.stderr)
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

            inv_items_count = save.inventory_count()

            # If --select argument provided, choose different selector
            if args['selection']:
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
            print(f'Running tool {meta.tool_name}...')

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
            final_inv_items_count = save.inventory_count()
            print_items = False
            for name, count in final_inv_items_count.items():
                if name not in inv_items_count or final_inv_items_count[name] > inv_items_count[name]:
                    print_items = True
                    break

            if print_items:
                print('Make sure you have the following items in your inventory before loading the map:')
                for name, count in final_inv_items_count.items():
                    print(f'{count:>9,}x {name}')
        case 'fix':
            filename = args['filename'].strip()
            path = os.path.abspath(os.path.expanduser(filename))
            if args['backend']:
                backend = parse_resource_backend(args['backend'])
            else:
                backend = CatboxBackend()  # default
            backup.fix_canvases(path, force_reupload=args['force'], backend=backend)
        case 'config':
            match args['config_mode']:
                case 'get':
                    if config_confirm_show():
                        print(config.get(args['key']))
                case 'set':
                    k, v = args['key'], ' '.join(args['value'])
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
                    if config_confirm_show():
                        for k, v in dict(config).items():
                            print(f'{k}: {v}')


if __name__ == '__main__':
    main()
