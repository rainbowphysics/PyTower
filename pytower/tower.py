from .selection import *
from .suitebro import Suitebro, ItemConnectionObject, TowerObject

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


def load_tools(verbose=False) -> list[str, ModuleType]:
    # Get tooling scripts
    tools_folder = 'pytower/tools'
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
        script_path = os.path.join(tools_folder, script)
        module_name = os.path.splitext(script)[0]
        if verbose:
            print(f"Loading tool script: {module_name}")
        try:
            spec = importlib.util.spec_from_file_location(module_name, script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            tool_name = module_name
            # Check if the module has a TOOL_NAME variable
            if hasattr(module, 'TOOL_NAME'):
                tool_name = getattr(module, 'TOOL_NAME')

            # Check if the module has a main function and call it
            if not hasattr(module, 'main'):
                logging.warning(f"No 'main' function found in tool '{tool_name}'. Skipping.")
                continue

            tools.append((tool_name, module))

        except Exception as e:
            logging.error(f"Error executing script '{script}': {e}")
            continue

    return tools


def parse_args(tool_names):
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
    #TODO fix bang and -j and -v flags to be whether they are inlcluded, not true/false
    parser.add_argument('-!', '--overwrite', dest='overwrite', type=bool, help='Tool to use')
    parser.add_argument('-', '--', '--params', '--parameters', dest='parameters', nargs='*',
                        help='Parameters to pass onto tooling script (must come at end)')
    parser.add_argument('-j', '--json', dest='json', type=bool, default=False,
                        help='If --json True, then to-json and to-save steps are skipped')

    if len(sys.argv) == 1:
        parser.print_help(sys.stdout)
        sys.exit(0)

    # Return args as a dict
    return vars(parser.parse_args())


def parse_selection(select_input: str) -> Selection:
    select_input = select_input.strip().casefold()
    if select_input == 'all' or select_input == 'everything':
        return ItemSelection()


def main(filename, tooling_injection: Callable[[Suitebro, list[TowerObject], list], None] = None,
         tools: list[str, ModuleType] = [], args: dict = None):
    # Make sure script is running in main directory, not tools directory (and not main module directory)
    if tooling_injection is not None:
        os.chdir(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

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

    if tooling_injection is not None:
        tooling_injection(save, save.objects, args['parameters'])
        args['overwrite'] = True

    # TODO apply selection and parse rest of args

    if 'tool' in args:
        for name, module in tools:
            if name.casefold().startswith(args['tool'].casefold()):
                module.main(save, save.objects, args['parameters'])

    with open(json_final_path, 'w') as fd:
        json.dump(save.to_dict(), fd, indent=2)

    # Finally run!
    run_suitebro_parser(json_final_path, True, final_output_path, overwrite=True)


def init():
    tools = load_tools(verbose=len(sys.argv) <= 1)
    tool_names = ', '.join([name for name, _ in tools])
    print()
    args = parse_args(tool_names)

    main(args['input'], tooling_injection=None, tools=tools, args=args)


if __name__ == '__main__':
    init()
