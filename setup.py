import importlib
import pkgutil
import os
import subprocess

import setuptools
from setuptools import setup
from setuptools.command.build_py import build_py
from distutils.util import convert_path
import logging

def run_command(args, error_context='Error'):
    try:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            print(line, end='')
        process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)
    except Exception as e:
        logging.error(f"{error_context}: {e}")


class CustomBuildCommand(build_py):
    def run(self):
        run_command(['git', 'clone', 'https://github.com/brecert/tower-unite-suitebro.git'],
                    error_context='Error cloning Suitebro repository')

        cwd = os.getcwd()
        os.chdir('tower-unite-suitebro')
        run_command(['git', 'pull'],
                    error_context='Error pulling from Suitebro repository')
        run_command(['cargo', 'build', '--release'],
                    error_context='Error building Rust binary')  # Assuming cargo is installed and in the PATH
        os.chdir(cwd)

        super().run()


with open('requirements.txt', 'r') as fd:
    requirements = fd.readlines()

spec = importlib.util.spec_from_file_location('pytower', convert_path('pytower/__init__.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
version = getattr(module, '__version__')
print(f'Installing PyTower {version}')

setup(
    name='pytower',
    version=version,
    description='Python API for Tower Unite map-editing',
    url='https://github.com/rainbowphysics/PyTower',
    author='Physics System',
    author_email='rainbowphysicsystem@gmail.com',
    license='MIT License',
    packages=setuptools.find_packages(),
    package_data={'pytower': ['tower-unite-suitebro/*']},
    install_requires=requirements,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pytower = pytower.tower:main'
        ]
    },

    cmdclass={
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
