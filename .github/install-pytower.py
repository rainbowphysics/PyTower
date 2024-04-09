import base64
import os
import pkgutil
import importlib.util
import subprocess
import sys
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

COLOR = False
if importlib.util.find_spec('colorama'):
    COLOR = True
    import colorama
    from colorama import Fore, Back, Style

    colorama.init(convert=sys.platform == 'win32')


def cancel():
    if COLOR:
        print(Fore.RED, end='')
    print(f'\nAborting PyTower {VERSION} install...')
    if COLOR:
        print(Style.RESET_ALL, end='')
    sys.exit(1)


def run_command(args, error_context='Error', can_fail=False):
    try:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                                   shell=True, cwd=os.getcwd())
        for line in process.stdout:
            print(line, end='')
        process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)
    except Exception as e:
        print(f'{error_context}: {e}', file=sys.stderr)
        if can_fail:
            sys.exit(1)


def main():
    print(f'Installing PyTower {VERSION}...\n')
    zip_file = base64.b64decode(ARCHIVE, validate=True)

    default_install_dir = os.path.join(os.path.join(os.path.expanduser('~'), 'PyTower'), f'pytower-{VERSION}')
    install_dir = input(f'Install directory for PyTower (leave blank for default {default_install_dir}):')
    install_dir = install_dir.strip()
    if install_dir is None or install_dir == '':
        install_dir = default_install_dir

    confirm = input(f'Install path: {install_dir}\nConfirm? (Y/n): ')
    confirm = confirm.strip()
    if confirm != 'y' and confirm != 'ye' and confirm != 'yes':
        cancel()

    # Commence install!
    os.makedirs(install_dir, exist_ok=True)
    os.chdir(install_dir)

    # Extract included zip
    zip_name = f'pytower-{VERSION}.zip'
    with open(zip_name, 'wb') as fd:
        fd.write(zip_file)

    with ZipFile(zip_name, 'r') as zipd:
        zipd.extractall('../')

    # Run its install.sh or install.bat depending on platform
    if sys.platform == 'win32' or sys.platform == 'cygwin':
        run_command('install.bat', can_fail=True)
    elif sys.platform == 'linux':
        run_command('./install.sh', can_fail=True)
    else:
        print(f'OS {sys.platform} not supported :(', file=sys.stderr)
        cancel()

    if COLOR:
        print(Fore.GREEN, end='')
    print(f'\nInstallation complete for PyTower v{VERSION} ~\n')
    if COLOR:
        print(Style.RESET_ALL, end='')


if __name__ == '__main__':
    main()
