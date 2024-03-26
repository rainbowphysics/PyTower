import subprocess
import textwrap

from pytower.util import xyz
from .selection import *
from .suitebro import Suitebro, TowerObject
from . import __version__

import argparse
import importlib
import json
import logging
from subprocess import Popen, PIPE
import sys
import os
from typing import Callable
from types import ModuleType


def run_suitebro_parser(input_path: str, to_save: bool, output_path: str | None = None, overwrite: bool = False):
    curr_cwd = os.getcwd()
    suitebro_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tower-unite-suitebro')
    os.chdir(suitebro_path)

    process = Popen(f'cargo run --release {"to-save" if to_save else "to-json"} {"-!" if overwrite else ""}'
                    f' -i \"{input_path}\" -o \"{output_path}\"', stdout=PIPE)
    (output, err) = process.communicate()
    print(output, file=sys.stderr)
    for line in output.splitlines(False):
        print(line)

    exit_code = process.wait()

    if exit_code != 0:
        logging.warning('Suitebro to-json did not complete successfully!')

    os.chdir(curr_cwd)


class ToolParameterInfo:
    def __init__(self, dtype=str, description='', optional=False):
        self.dtype = dtype
        self.description = description
        self.optional = optional


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
            param_str = '\n\nRequired parameters:'
            for name, info in self.params.items():
                param_str += f'\n  {name}:{info.dtype.__name__} - {info.description}'

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


def load_tool(tools_folder, script, verbose=False) -> tuple[ModuleType, ToolMetadata] | None:
    script_path = os.path.join(tools_folder, script)
    module_name = os.path.splitext(script)[0]
    if verbose:
        print(f"Loading tool script: {module_name}")
    try:
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
        logging.error(f"Error executing script '{script}': {e}")


def load_tools(verbose=False) -> list[ModuleType, ToolMetadata]:
    # Get tooling scripts
    tools_folder = 'tools'
    if not os.path.exists(tools_folder):
        os.mkdir(tools_folder)

    files = os.listdir(tools_folder)

    python_files = [f for f in files if f.endswith('.py')]
    if not python_files:
        logging.warning("No Python scripts found in 'tools' folder.")
        return []

    # Execute each Python script
    tools = []
    for script in python_files:
        load_result = load_tool(tools_folder, script, verbose=verbose)
        if load_result is None:
            continue
        tools.append(load_result)

    return tools


class Subcommand:
    def __init__(self, name: str, num_args: int, func: Callable):
        self.name = name
        self.num_args = num_args
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def parse_args(tools: list[ModuleType, ToolMetadata], tool_names):
    parser = argparse.ArgumentParser(prog='PyTower',
                                     description='High-level toolset and Python API for Tower Unite map editing',
                                     epilog=f'Detected tools: {tool_names}')
    parser.add_argument('-i', '--input', dest='input', type=str, default='CondoData',
                        help='Input file')
    parser.add_argument('-o', '--output', dest='output', type=str, default='CondoData_output',
                        help='Output file')
    parser.add_argument('-s', '--select', dest='selection', type=str, default='everything',
                        help='Selection type')
    parser.add_argument('-v', '--invert', dest='invert', type=bool, default=False,
                        help='Whether or not to invert selection')
    parser.add_argument('-t', '--tool', dest='tool', type=str,
                        help=f'Tool script to use')
    # TODO fix bang and -j and -v flags to be whether they are inlcluded, not true/false
    parser.add_argument('-!', '--overwrite', dest='overwrite', type=bool, help='Tool to use')
    parser.add_argument('-', '--', '--params', '--parameters', dest='parameters', nargs='*',
                        help='Parameters to pass onto tooling script (must come at end)')
    parser.add_argument('-j', '--json', dest='json', type=bool, default=False,
                        help='If --json True, then to-json and to-save steps are skipped')

    # Subcommands
    if len(sys.argv) == 1:
        parser.print_help(sys.stdout)
        sys.exit(0)

    if len(sys.argv) == 2:
        subcmd = sys.argv[-1]
        if subcmd.endswith('version'):
            print(f'PyTower {__version__}')
            sys.exit(0)

        if subcmd.endswith('info'):
            print(f'Usage: pytower info <tool_name>. \n\n Available tools: {tool_names}')
            sys.exit(0)

    if len(sys.argv) == 3 and sys.argv[1].endswith('info'):
        tool_name = sys.argv[2].strip().casefold()
        for _, meta in tools:
            if meta.tool_name.casefold() == tool_name:
                print(meta.get_info())
                sys.exit(0)

        logging.error(f'Could not find {sys.argv[2]}! \n\n Available tools: {tool_names}')
        sys.exit(1)

    return vars(parser.parse_args())


def parse_selection(select_input: str) -> Selection:
    select_input = select_input.strip().casefold()
    if select_input == 'all' or select_input == 'everything':
        return ItemSelection()


def parse_parameters(param_input: list[str], meta: ToolMetadata) -> dict:
    # Ensure that all inputs were parsed correctly as strings
    params = {}
    for param in param_input:
        if not isinstance(param, str):
            logging.error(f'Invalid parameter: {param}.\n\nShould have format "parameter=value" with no spaces.')
            sys.exit(1)

        param_split = param.strip().casefold().split('=')
        if len(param_split) != 2:
            logging.error(f'Invalid parameter: {param}.\n\nShould have format "parameter=value" with no spaces and only'
                          f'one equal sign.')
            sys.exit(1)

        param_name, value = param_split
        if param_name in meta.params:
            # Typecast value to expected type
            value = meta.params[param_name].dtype(value)

        params[param_name] = value

    # Make the user input any other required parameters
    for param, info in meta.params.items():
        if not info.optional and param not in params:
            value = input(f'Enter value for {param.lower()}: ')
            try:
                value = info.dtype(value)
            except Exception as e:
                print(f'Invalid value for {param.lower()}: {e}')
                sys.exit(1)
            params[param] = value

    return params


def main(filename, tooling_injection: Callable[[Suitebro, list[TowerObject], dict], None] = None,
         tools: list[ModuleType, ToolMetadata] = [], args: dict = None):
    # TODO remove this chdir fuckery and just let the code run wherever it happens to run, including in the tools
    #  directory
    # Make sure script is running in main directory, not tools directory (and not main module directory)
    if tooling_injection is not None:
        # Setup mocking
        tool_file = tooling_injection.__globals__['__file__']
        mock_tool, mock_metadata = load_tool(os.path.dirname(tool_file), os.path.basename(tool_file), verbose=True)
        mock_params = parse_parameters(args['parameters'], mock_metadata)

        # By default, mocked tool scripts overwrite files for rapid prototyping
        if 'overwrite' not in args:
            args['overwrite'] = True

    # TODO apply selection and validate args

    # TODO fix this up using args['output']
    abs_filepath = os.path.realpath(filename)
    condo_dir = os.path.dirname(abs_filepath)
    json_output_path = os.path.join(condo_dir, os.path.basename(abs_filepath) + ".json")
    json_final_path = os.path.join(condo_dir, f'{filename}_output.json')
    final_output_path = os.path.join(condo_dir, f'{filename}_output')

    run_suitebro_parser(abs_filepath, False, json_output_path, overwrite=True)

    os.chdir(condo_dir)

    print('Loading JSON file...')
    with open(json_output_path, 'r') as fd:
        save_json = json.load(fd)

    save = Suitebro(save_json)

    # Run any injected tooling script
    if tooling_injection is not None:
        logging.info(f'Running {mock_metadata.tool_name} with parameters {mock_params}')
        tooling_injection(save, ItemSelection().select(save.objects), mock_params)

    if 'tool' in args:
        for module, meta in tools:
            if meta.tool_name.casefold().startswith(args['tool'].casefold()):
                params = parse_parameters(args['parameters'], meta)
                logging.info(f'Running {meta.tool_name} with parameters {params}')
                module.main(save, save.objects, params)
                break

    with open(json_final_path, 'w') as fd:
        json.dump(save.to_dict(), fd, indent=2)

    # Finally run!
    run_suitebro_parser(json_final_path, True, final_output_path, overwrite=True)


def init():
    tools = load_tools()
    tool_names = ', '.join([meta.tool_name for _, meta in tools])
    args = parse_args(tools, tool_names)

    main(args['input'], tooling_injection=None, tools=tools, args=args)


if __name__ == '__main__':
    init()
