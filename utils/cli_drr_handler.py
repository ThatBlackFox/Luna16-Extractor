import os
from utils.drr_maker import process_mhd_folder

mandate = ['-d', '-o', '-m']
DATA_DIR = ""
OUTPUT_DIR = ""
MASK_DIR = ""

def check_args(args: list):
    for arg in mandate:
        if not arg in args:
            raise ValueError(f"{arg} is a mandatory keyword, use -h for help")

def print_help():
    help_message = """\033[1;36m
CT Patch Extractor - Help
\033[0m
Usage:
  python dataset_maker.py -d <data_directory> -o <output_directory> [-c <csv_file>]

\033[1;33mOptions:\033[0m
  \033[1;32m-d\033[0m    Path to the directory containing full chest CT scans (.mhd)  \033[1;30m[Required]\033[0m
  \033[1;32m-o\033[0m    Output directory to store extracted CT patches                \033[1;30m[Required]\033[0m
  \033[1;32m-c\033[0m    Path to the CSV file containing annotations (optional)

\033[1;33mExample Usage:\033[0m
  \033[1;34mpython script.py -d /path/to/ct_scans -o /path/to/output\033[0m
  \033[1;34mpython script.py -d /path/to/ct_scans -o /path/to/output -c annotations.csv\033[0m

\033[1;35mDescription:\033[0m
  This script extracts patches from chest CT scans stored in the specified directory.
  If an annotation CSV file is provided, patches will be extracted based on its coordinates.
  Else the script expects an annotation CSV file in the data directory.
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
    global MASK_DIR
    DATA_DIR = args[args.index('-d')+1]
    OUTPUT_DIR = args[args.index('-o')+1]
    MASK_DIR = args[args.index('-m')+1]

def start_patch():
    data = {
        "data":DATA_DIR,
        "mask":MASK_DIR,
        "out": OUTPUT_DIR,
    }
    process_mhd_folder(data['data'], os.path.join(OUTPUT_DIR, "full_ct_xray"))
    process_mhd_folder(data['mask'], os.path.join(OUTPUT_DIR, "full_ct_mask"))
    

def main(args: list):
    checks(args)
    set_vars(args)
    start_patch()