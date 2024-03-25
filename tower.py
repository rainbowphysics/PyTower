import argparse
import importlib
import json
import logging
from subprocess import Popen, PIPE
import sys
import os
from typing import Callable

from suitebro import Suitebro, ItemConnectionObject, TowerObject
from types import ModuleType

SUITEBRO_PATH = r'C:\Users\gklub\Documents\Tower Unite\suitebro'


def run_suitebro_parser(input_path: str, to_save: bool, output_path: str | None = None, overwrite: bool = False):
    curr_cwd = os.getcwd()
    os.chdir(SUITEBRO_PATH)

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

def load_tools() -> list[str, ModuleType]:
    # Get tooling scripts
    tools_folder = 'tools'
    if not os.path.exists(tools_folder):
        os.mkdir(tools_folder)

    files = os.listdir(tools_folder)

    python_files = [f for f in files if f.endswith('.py')]
    if not python_files:
        print("No Python scripts found in 'tools' folder.")
        return []

    # Execute each Python script
    tools = []
    for script in python_files:
        script_path = os.path.join(tools_folder, script)
        module_name = os.path.splitext(script)[0]
        print(f"Loading script: {module_name}")
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
                print(f"No 'main' function found in tool '{tool_name}'. Skipping.")
                continue

            tools.append(tool_name, module)

        except Exception as e:
            print(f"Error executing script '{script}': {e}")


def parse_args(tool_names):
    parser = argparse.ArgumentParser(description='Entrypoint for TowerPy')
    parser.add_argument('-i', '--input', dest='input', type=str, default='CondoData',
                        help='Input file')
    parser.add_argument('-o', '--output', dest='output', type=str, default='CondoData_output',
                        help='Output file')
    parser.add_argument('-s', '--select', dest='selection', type=str, default='everything',
                        help='Selection type')
    parser.add_argument('-v', '--invert', dest='invert', type=bool, default=False,
                        help='Whether or not to invert selection')
    parser.add_argument('-t', '--tool', dest='tool', type=str,
                        help=f'Tool script to use. Available tools: {tool_names}')
    parser.add_argument('-!', '--overwrite', dest='overwrite', type=bool, help='Tool to use')
    parser.add_argument('-', '--', '--params', '--parameters', dest='parameters', nargs='*',
                        help='Parameters to pass onto tooling script (must come at end)')
    # Return args as a dict
    return vars(parser.parse_args())

def main(filename, tooling_injection: Callable[[Suitebro, list[TowerObject], list], None] = None,
         tools: list[str, ModuleType] = [], args: dict = None):
    # Make sure script is running in main directory, not tools directory
    if tooling_injection is not None:
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

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
    '''
    exclusions = ['CanvasWallFull', 'Counter', 'FloatingTextSign']
    template_objects = list(
        filter(lambda obj: (obj.item is not None) and (obj.item['name'] not in exclusions), save.objects))
    print(template_objects)

    for x in range(-5, 5):
        for y in range(-5, 5):
            for z in range(20):
                if x == 0 and y == 0 and z == 0:
                    continue
                copies = TowerObject.copy_group(template_objects)

                # Set position
                for obj in copies:
                    obj.item['position']['x'] += 70 * x
                    obj.item['position']['y'] += 70 * y
                    obj.item['position']['z'] += 70 * z

                save.add_objects(copies)
    '''

    with open(json_final_path, 'w') as fd:
        json.dump(save.to_dict(), fd, indent=2)

    # Finally run!
    run_suitebro_parser(json_final_path, True, final_output_path, overwrite=True)


if __name__ == '__main__':
    tools = load_tools()

    tool_names = ', '.join([name for name, _ in tools])
    args = parse_args(tool_names)

    main(args['input'], tooling_injection=None, tools=tools, args=args)
