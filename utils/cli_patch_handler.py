import os
from utils.patching import patching

mandate = ['-d', '-r', '-o']
DATA_DIR = ""
REF_DIR = ""
OUTPUT_DIR = ""
META_PATH = ""

def check_args(args: list):
    for arg in mandate:
        if not arg in args:
            raise ValueError(f"{arg} is a mandatory keyword, use -h for help")

def print_help():
    help_message = """\033[1;36m
Dataset Patcher - Help
\033[0m
Usage:
  python dataset_patcher.py -d <data_directory> -r <reference_directory> -o <output_directory> [-m <meta.json>]

\033[1;33mOptions:\033[0m
  \033[1;32m-d\033[0m    Path to the directory containing full chest CT scans           \033[1;30m[Required]\033[0m
  \033[1;32m-r\033[0m    Path to the reference directory containing segmentation masks  \033[1;30m[Required]\033[0m
  \033[1;32m-o\033[0m    Output directory where patched segmentation masks will be saved  \033[1;30m[Required]\033[0m
  \033[1;32m-m\033[0m    Path to the meta.json file generated during dataset creation    \033[1;30m[Optional]\033[0m

\033[1;33mExample Usage:\033[0m
  \033[1;34mpython dataset_patcher.py -d /path/to/ct_scans -r /path/to/masks -o /path/to/output\033[0m
  \033[1;34mpython dataset_patcher.py -d /path/to/ct_scans -r /path/to/masks -o /path/to/output -m meta.json\033[0m

\033[1;35mDescription:\033[0m
  This script aligns segmentation masks with their corresponding CT scans.
  It resizes and adjusts the segmentation masks to match the full-size CT scans.
  If a meta.json file is provided, the script will use it for additional metadata handling.
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
    global REF_DIR
    global OUTPUT_DIR
    global META_PATH
    DATA_DIR = args[args.index('-d')+1]
    OUTPUT_DIR = args[args.index('-o')+1]
    REF_DIR = args[args.index('-r')+1]
    if "-m" in args:
        META_PATH = args[args.index('-m')+1]
    else:
        META_PATH = os.path.join(DATA_DIR, 'meta.json')

def start_patch():
    data = {
        "data":DATA_DIR,
        "out": OUTPUT_DIR,
        "ref": REF_DIR,
        "meta": META_PATH
    }
    patching(data)
    

def main(args: list):
    checks(args)
    set_vars(args)
    start_patch()