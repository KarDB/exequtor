import argparse
import sys
from generate_instructions import make_yaml_files_for_sweeps
from datetime import datetime
import ruamel.yaml
yaml = ruamel.yaml.YAML(typ='safe')
yaml.preserve_quotes = True

def executor_argparse() -> argparse.Namespace:
   parser2 = argparse.ArgumentParser(
       description='Handles optimized sweep measurements with Qupyt')
   parser2.add_argument('action',
                      help='Choose what to do',
                      choices=['start_sweeps','start_analysis'])
   parser2.add_argument('--file', '-f', help="File to print", required=False)
   arguments = parser2.parse_args(sys.argv[1:])
   sys.argv = ['qupyt']
   print(arguments)
   return arguments


def main():
    """Match through argparse arguments to determine course of action"""
    arguments = executor_argparse()
    match arguments.action:
        case 'start_sweeps':
            with open(arguments.file, 'r', encoding='utf-8') as file:
                filedata = yaml.load(file)
                optimized_params = {}
                for key in filedata.keys():
                    make_yaml_files_for_sweeps(filedata, key, optimized_params)
                    input("Klick enter to proceed with the next measurement look")
                #save_optimized_values()
        case 'start_analysis':
            pass
        case _:
            print('invalid option')


if __name__ == '__main__':
    main()

# make_yaml_files_for_sweeps
