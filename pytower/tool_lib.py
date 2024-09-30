import collections
import json
import pkgutil
import importlib.util
import importlib
import sys
from types import ModuleType
from typing import Any, Callable, TypeVar, overload

from .logging import *
from .selection import Selection
from .suitebro import Suitebro
from .util import not_none, xyz, xyz_to_string, xyzint


class ToolParameterInfo:
    def __init__(self, dtype: Callable[[Any], Any] = str, description: str='', default: Any=None):
        self.dtype = dtype
        self.description = description
        self.default = default

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        data['dtype'] = self.dtype.__name__
        data['description'] = self.description

        if self.default is not None and (self.dtype == xyz or self.dtype == xyzint):
            data['default'] = xyz_to_string(self.default)
        else:
            data['default'] = self.default
        return data

    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'ToolParameterInfo':
        # Define conversion to/from registered parameter types
        type_table = {'str': str, 'bool': bool, 'int': int, 'float': float, 'xyz': xyz, 'xyzint': xyzint}

        # Load values
        dtype = type_table[data['dtype']]
        description = data['description']
        default = dtype(data['default']) if 'default' in data and data['default'] is not None else None

        return ToolParameterInfo(dtype, description, default)


class ToolMetadata:
    def __init__(self, tool_name: str, params: dict[str, ToolParameterInfo], version: str | None, author: str | None, url: str | None,
                 info: str | None, hidden: bool = False, nowrite: bool = False):
        self.tool_name = tool_name
        self.params = params
        self.version = version
        self.author = author
        self.url = url
        self.info = info
        self.hidden = hidden
        self.nowrite = nowrite

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

    T = TypeVar('T')
    @staticmethod
    def attr_or_default(module: object, attr: str, default: T) -> T:
        if hasattr(module, attr):
            return getattr(module, attr)

        return default

    @overload
    @staticmethod
    def strattr_or_default(module: object, attr: str, default: str) -> str: ...

    @overload
    @staticmethod
    def strattr_or_default(module: object, attr: str, default: str | None) -> str | None: ...

    @staticmethod
    def strattr_or_default(module: object, attr: str, default: str | None) -> str | None:
        if hasattr(module, attr):
            return str(getattr(module, attr)).strip()

        return default

    def to_dict(self) -> dict[str, Any]:
        data = {varname: value for (varname, value) in vars(self).items() if varname != 'params' and value is not None}

        # Special handling for parameters
        data['params'] = {}  # Need fresh dictionary, make sure pointers dont get shared
        for p_name, p_info in self.params.items():
            data['params'][p_name] = p_info.to_dict()

        return data

    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'ToolMetadata':
        # Convert the input dict into a defaultdict so that missing entries become None
        data_or_none = collections.defaultdict(lambda: None, data)
        data_or_false = collections.defaultdict(lambda: False, data)
        tool_name = data_or_none['tool_name']
        version = data_or_none['version']
        author = data_or_none['author']
        url = data_or_none['url']
        tool_info = data_or_none['info']
        hidden = data_or_false['hidden']
        nowrite = data_or_false['nowrite']

        # Handle parameter list
        params: dict[str, Any] = data_or_none['params'] or {}
        for p_name, p_info_dict in params.items():
            params[p_name] = ToolParameterInfo.from_dict(p_info_dict)

        return ToolMetadata(not_none(tool_name), params, version, author, url, tool_info, hidden, nowrite)


class ParameterDict(dict[str, Any]):
    def __getattr__(self, key: str):
        if key in self:
            return self[key]
        else:
            raise AttributeError(f"'ParameterDict' object has no attribute '{key}'")


ToolMainType = Callable[[Suitebro, Selection, ParameterDict], None]
ToolListType = list[tuple[ModuleType, ToolMetadata]]
PartialToolListType = list[tuple[ModuleType | str, ToolMetadata]]


def load_tool(script_path: str) -> tuple[ModuleType, ToolMetadata] | None:
    script = os.path.basename(script_path)
    module_name = os.path.splitext(script)[0]
    info(f'Loading tool script: {module_name}')
    try:
        # TODO convert from importlib.util to pkgutil
        spec = not_none(importlib.util.spec_from_file_location(module_name, script_path))
        module = importlib.util.module_from_spec(spec)
        not_none(spec.loader).exec_module(module)

        # Get script directives/metadata variables
        tool_name = ToolMetadata.strattr_or_default(module, 'TOOL_NAME', module_name)
        params = ToolMetadata.attr_or_default(module, 'PARAMETERS', dict[str, ToolParameterInfo]())
        version = ToolMetadata.strattr_or_default(module, 'VERSION', None)
        author = ToolMetadata.strattr_or_default(module, 'AUTHOR', None)
        url = ToolMetadata.strattr_or_default(module, 'URL', None)
        tool_info = ToolMetadata.strattr_or_default(module, 'INFO', None)
        hidden = ToolMetadata.attr_or_default(module, 'HIDDEN', False)
        nowrite = ToolMetadata.attr_or_default(module, 'NO_WRITE', False)

        # Check if the module has a main function before registering it
        if not hasattr(module, 'main') and not hidden:
            error(f"No 'main' function found in tool '{tool_name}'. Skipping.")
            return None

        success_message = f'Successfully loaded {tool_name}'
        if version is not None:
            success_message += f' {version}'
        if author is not None:
            success_message += f' by {author}'

        if not hidden:
            success(success_message)

        return module, ToolMetadata(tool_name, params, version, author, url, tool_info, hidden, nowrite)

    except Exception as e:
        error(f"Error loading tool '{script}': {e}")


TOOLS_PATH = os.path.join(root_directory, 'tools')
TOOLS_INDEX_NAME = 'tools-index.json'
TOOLS_INDEX_PATH = os.path.join(root_directory, TOOLS_INDEX_NAME)


def make_tools_index(tools: PartialToolListType):
    tools_dict: dict[str, Any] = {}
    for module_or_path, meta in tools:
        # Convert tool metadata to dictionary
        tool_data = meta.to_dict()

        # Get path name
        if isinstance(module_or_path, ModuleType):
            tool_path = not_none(module_or_path.__file__)
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
        error("No Python scripts found in 'tools' folder.")
        return []

    python_files = sorted(python_files)

    # Convert to absolute paths and return
    return [os.path.normcase(os.path.join(TOOLS_PATH, filename)) for filename in python_files]


def get_indexed_tools() -> PartialToolListType | None:
    try:
        with open(TOOLS_INDEX_PATH, 'r') as fd:
            tools_index = json.load(fd)
    except (OSError, json.JSONDecodeError):
        warning('Failed to load tools index... Will regenerate')
        return None

    output_tools = PartialToolListType()
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
                warning(f'Failed to load tool from index: {tool_path}')
                continue

            output_tools.append(tool_tuple)
        else:
            output_tools.append((tool_path, ToolMetadata.from_dict(meta_dict)))

    # Process any added tools
    for script_path in get_tool_scripts():
        # If tool not found in index, load and add it
        if script_path not in tools_index:
            info(f'NEW TOOL SCRIPT DETECTED: {os.path.basename(script_path)} (located in '
                  f'{os.path.dirname(script_path)})')
            response = input('Are you sure you want to trust this script? (Y/n)\n').strip().casefold()
            if response == 'y' or response == 'ye' or response == 'yes':
                tool_tuple = load_tool(script_path)
                if tool_tuple is None:
                    error(f'Failed to load tool: {script_path}')
                    continue
            else:
                info('Aborting program.')
                sys.exit(0)

            output_tools.append(tool_tuple)

    # Sort tools alphabetically by tool name
    output_tools.sort(key=lambda tool_tuple: tool_tuple[-1].tool_name)
    return output_tools


def load_tools() -> PartialToolListType:
    # First load the index
    info('Loading index file...')
    tools_index = get_indexed_tools()

    # If we were successful in loading the tools index, perfect we're done!
    if tools_index:
        make_tools_index(tools_index)
        return tools_index

    # First time execution!
    # Get all tooling scripts
    if not os.path.exists(TOOLS_PATH):
        os.mkdir(TOOLS_PATH)

    tool_paths = get_tool_scripts()

    # Append each successfully loaded tool to the output
    tools: PartialToolListType = []
    for path in tool_paths:
        load_result = load_tool(path)
        if load_result is None:
            continue
        tools.append(load_result)

    # Create index for future execution
    make_tools_index(tools)

    return tools
