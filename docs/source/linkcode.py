# the sphinx extension 'sphinx.ext.viewcode' links documentation to an online
# code repository but requires to bind the code to the url through a user
# specific `linkcode_resolve` function. This implementation should be fairly
# generic and easily adaptable.
#
# License: Public Domain, CC0 1.0 Universal (CC0 1.0)

# Forked by Physics System (May, 2024): https://gist.github.com/rainbowphysics/505e35a7a1e9545d5a6cde22f6ca9558

import sys
import os
import subprocess
import inspect

# Link to your GitHub repo here:
REPO_LINK = 'https://github.com/rainbowphysics/PyTower'
# Specify main branch
MAIN_BRANCH = 'main'


def run_git_command(cmd: str) -> str | None:
    try:
        # Run command and get the output
        output: str = subprocess.check_output(cmd.split()).strip().decode('utf-8')

        # In case command failed, return None
        if output.startswith('fatal:'):
            return None

        # Return the raw command output
        return output
    except subprocess.CalledProcessError:
        return None


# lock to current commit number
head_commit = run_git_command('git log -n1 --pretty=%H')
if head_commit is not None:
    linkcode_revision = head_commit

    # if we are on main's HEAD, use main as reference instead
    main_head_commit = run_git_command(f'git log --first-parent {MAIN_BRANCH} -n1 --pretty=%H')
    if head_commit == main_head_commit:
        linkcode_revision = MAIN_BRANCH

    # if we have a tag, use tag as reference
    tag = run_git_command(f'git describe --exact-match --tags {linkcode_revision}')
    if tag is not None:
        linkcode_revision = tag

else:
    # If for some reason git command didn't work then default to main branch
    linkcode_revision = MAIN_BRANCH


def get_line_range(obj):
    source, lineno = inspect.getsourcelines(obj)
    return lineno, lineno + len(source) - 1


def get_link_info(modname: str, fullname: str) -> tuple[str, tuple[int, int]] | tuple[str, None]:
    # Fallback in case git repo is missing or malformed, or another error occurs
    fallback = modname.replace('.', '/')

    # Get module based on module name
    module = sys.modules.get(modname)
    if module is None:
        return fallback, None

    repo_main_folder = run_git_command('git rev-parse --show-toplevel')
    if repo_main_folder is None:
        return fallback, None

    parent_obj = None
    obj = module
    for part in fullname.split('.'):
        try:
            next_obj = getattr(obj, part)
            parent_obj = obj
            obj = next_obj
        except AttributeError:
            return fallback, None

    if isinstance(obj, property):
        obj = obj.fget

    try:
        src_file = inspect.getsourcefile(obj)
    except TypeError:
        src_file = inspect.getsourcefile(parent_obj)

    filepath = os.path.relpath(src_file, repo_main_folder)

    try:
        source, lineno = inspect.getsourcelines(obj)
        linestart, linestop = lineno, lineno + len(source) - 1
    except OSError:
        return filepath, None
    except TypeError:
        source, lineno = inspect.getsourcelines(parent_obj)
        found_in_source = False
        for idx, line in enumerate(source):
            if line.startswith(fullname.split('.')[-1]):
                linestart = lineno + idx
                linestop = linestart
                found_in_source = True
                break

        if not found_in_source:
            return filepath, None

    return filepath, (linestart, linestop)


def linkcode_resolve(domain, info):
    if domain != 'py' or not info['module']:
        return None

    filepath, linenos = get_link_info(info['module'], info['fullname'])
    result = f'{REPO_LINK}/blob/{linkcode_revision}/{filepath}'
    if linenos is not None:
        linestart, linestop = linenos
        result += f'#L{linestart}-L{linestop}'

    return result