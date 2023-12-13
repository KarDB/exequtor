import argparse

from executor.generate_instructions import make_yaml_files_for_sweeps

parser = argparse.ArgumentParser(
    description='Handle measurement folder and live lab logs')
parser.add_argument('action',
                    help='Choose what to do',
                    choices=['start_sweeps'] )

parser.add_argument('--file', '-f', help="File to print", required=False)

args = parser.parse_args()

def main():
    """Match through argparse arguments to determine course of action"""
    match args.action:
        case 'start_sweeps': make_yaml_files_for_sweeps(args.file)
        case _: print('invalid option')

if __name__ == '__main__':
    main()

#make_yaml_files_for_sweeps
