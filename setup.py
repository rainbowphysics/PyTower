import os
import subprocess
from setuptools import setup
from setuptools.command.install import install


def install_dependencies():
    try:
        subprocess.run(['git', 'clone', 'https://github.com/brecert/tower-unite-suitebro.git'])
    except Exception as e:
        print(f"Error cloning repository: {e}")


class CustomInstallCommand(install):
    def run(self):
        install_dependencies()

        cwd = os.getcwd()
        os.chdir('tower-unite-suitebro')
        subprocess.run(['cargo', 'build', '--release'])  # Assuming cargo is installed and in the PATH
        os.chdir(cwd)

        install.run(self)


setup(
    name='pytower',
    version='0.1.0',
    description='Python API for Tower Unite map-editing',
    url='https://github.com/kluberge/PyTower',
    author='Physics System',
    author_email='rainbowphysicsystem@gmail.com',
    license='MIT License',
    packages=['pytower'],
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'pytower = pytower.tower:main'
        ]
    },

    cmdclass={
        'install': CustomInstallCommand
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
