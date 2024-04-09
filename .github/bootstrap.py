import base64
from argparse import ArgumentParser


def main():
    # Basic argpase
    parser = ArgumentParser(prog='bootstrap', description='Install script bootstrapper')
    parser.add_argument('-i', '--input', dest='input', type=str, help='Input file path', required=True)
    parser.add_argument('-v', '--version', dest='version', type=str, help='Version', required=True)
    parser.add_argument('-z', '--zip', dest='zip', type=str, help='Path to zip archive', required=True)
    args = parser.parse_args()

    # Open up the install script and zip
    with open(args.input, 'r') as fd:
        source_code = fd.readlines()
    with open(args.zip, 'rb') as fd:
        archive = fd.read()

    # Convert zip into base64 blob
    encoded = base64.b64encode(archive).decode()

    # Define VERSION and ARCHIVE variables in install-pytower.py script
    source_code = [f"VERSION = '{args.version}'\n", f"ARCHIVE = '{encoded}'\n"] + source_code

    # Write as version-specific install script
    with open(f'install-pytower-{args.version}.py', 'w') as fd:
        fd.writelines(source_code)


if __name__ == '__main__':
    main()
