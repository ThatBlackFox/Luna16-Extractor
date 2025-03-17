import os
from utils.patching import extracting
from pathlib import Path

mandate = ['-d', '-o', '-c']
DATA_DIR = ""
OUTPUT_DIR = ""
CSV_PATH = ""

def check_args(args: list):
    for arg in mandate:
        if not arg in args:
            raise ValueError(f"{arg} is a mandatory keyword, use -h for help")

def print_help():
    help_message = """\033[1;36m
CT Patch Extractor - Help
\033[0m
Usage:
  python multi_extract.py -d <data_directory> -o <output_directory> -c <csv_file>

\033[1;33mOptions:\033[0m
  \033[1;32m-d\033[0m    Path to the folder containing subfolders of CT scan subsets  \033[1;30m[Required]\033[0m
  \033[1;32m-o\033[0m    Empty folder where output for each subset will be stored in separate subfolders  \033[1;30m[Required]\033[0m
  \033[1;32m-c\033[0m    Path to the LUNA16 annotations CSV file                         \033[1;30m[Required]\033[0m

\033[1;33mExample Usage:\033[0m
  \033[1;34mpython script.py -d /path/to/ct_subsets -o /path/to/output -c luna16_annotations.csv\033[0m

\033[1;35mDescription:\033[0m
  This script extracts patches from chest CT scans stored in the specified directory.
  The scans should be organized in subfolders within the given data directory.
  The output will be stored in separate folders inside the specified output directory.
  The LUNA16 annotations CSV file is mandatory for extracting patches based on coordinates.
    """
    print(help_message)

def check_help(args: list):
    if '-h' in args:
        print_help()
        return False
    return True


def checks(args: list):
    if not check_help(args):
        exit(0)
    check_args(args)

def set_vars(args: list):
    global DATA_DIR
    global OUTPUT_DIR
    global CSV_PATH
    DATA_DIR = args[args.index('-d')+1]
    OUTPUT_DIR = args[args.index('-o')+1]
    if "-c" in args:
        CSV_PATH = args[args.index('-c')+1]
    else:
        CSV_PATH = os.path.join(DATA_DIR, 'annotations.csv')

def return_subsets():
    path = Path(DATA_DIR)
    subsets = [d.name for d in path.iterdir() if d.is_dir()]
    return subsets

def generate_args(subsets):
    args = []
    for subset in subsets:
        os.makedirs(os.path.join(DATA_DIR, subset), exist_ok=True)
        sub_args = {"data": os.path.join(DATA_DIR, subset), "out": os.path.join(DATA_DIR, subset), "csv": CSV_PATH}
        args.append(sub_args)
    return args
    

def main(args: list):
    checks(args)
    set_vars(args)
    subsets = return_subsets()
    return generate_args(subsets)
