import importlib
import pkgutil
import os
import subprocess
import sys

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.build_py import build_py
from distutils.util import convert_path
import logging


def run_command(args, error_context='Error', can_fail=False, shell=False):
    try:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                                   shell=shell)
        for line in process.stdout:
            print(line, end='')
        process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)
    except Exception as e:
        logging.error(f"{error_context}: {e}")
        if can_fail:
            sys.exit(1)


def get_suitebro_parser():
    run_command(['git', 'clone', 'https://github.com/brecert/tower-unite-suitebro.git'],
                error_context='Error cloning Suitebro repository')

    cwd = os.getcwd()

    # Exit if git clone failed (i.e., git is not installed or repo details have changed)
    try:
        os.chdir('tower-unite-suitebro')
    except OSError:
        raise SystemExit(1, 'Failed to install suitebro parser https://github.com/brecert/tower-unite-suitebro.git')

    # In case repo is already present, make sure it's up to date
    run_command(['git', 'pull'], error_context='Error pulling from Suitebro repository')

    run_command(['git', 'checkout', '1a90045f16c58a856e941b78f857560d0b5ce5de'],
                error_context='Error checking out non-uesave version')

    # Assuming cargo is installed and in the PATH
    run_command(['cargo', 'build', '--release'], error_context='Error building Rust binary', can_fail=True)

    os.chdir(cwd)


def is_junction(path: str) -> bool:
    try:
        return bool(os.readlink(path))
    except OSError:
        return False


def make_tools_symlink():
    cwd = os.getcwd()
    os.chdir('pytower')

    # Do nothing if symlink already exists
    if os.path.islink('tools') or is_junction('tools'):
        os.chdir(cwd)
        return

    # Create a junction on Windows and symlink on Unix
    args = ['mklink', '/J', 'tools', '..\\tools'] if sys.platform == 'win32' else ['ln', '-sf', '../tools', 'tools']
    run_command(args, error_context='Error creating symlink', can_fail=True, shell=True)

    # Change cwd back
    os.chdir(cwd)


def install(from_src=False):
    print(f'Installing PyTower {version}')

    # Build/install Suitebro parser
    if from_src:
        get_suitebro_parser()

    # Make symlink for `import pytower.tools`
    make_tools_symlink()


class CustomDevelopBuildCommand(develop):
    user_options = develop.user_options + [
        ('src', None, 'build from source'),
    ]

    def initialize_options(self):
        develop.initialize_options(self)
        self.src = 0

    def finalize_options(self):
        develop.finalize_options(self)

    def run(self):
        from_src = self.src == 1
        install(from_src=from_src)
        develop.run(self)


class CustomBuildCommand(build_py):
    user_options = build_py.user_options + [
        ('src', None, 'build from source'),
    ]

    def initialize_options(self):
        build_py.initialize_options(self)
        self.src = 0

    def finalize_options(self):
        build_py.finalize_options(self)

    def run(self):
        build_py.run(self)
        from_src = self.src == 1
        install(from_src=from_src)


with open('requirements.txt', 'r') as fd:
    requirements = fd.readlines()

spec = importlib.util.spec_from_file_location('pytower', convert_path('pytower/__init__.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
version = getattr(module, '__version__')

setup(
    name='pytower',
    version=version,
    description='Python API for editing CondoData/.map files',
    url='https://github.com/rainbowphysics/PyTower',
    author='Physics System',
    author_email='rainbowphysicsystem@gmail.com',
    license='MIT License',
    packages=['pytower', 'pytower.connections', 'pytower.tools'],
    install_requires=requirements,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pytower = pytower.tower:main'
        ]
    },

    cmdclass={
        'develop': CustomDevelopBuildCommand,
        'build_py': CustomBuildCommand
    },

    # https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: File Formats :: JSON',
        'Topic :: Games/Entertainment'
    ]
)
