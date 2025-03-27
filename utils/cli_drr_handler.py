import os
from utils.drr_unet_maker import *

mandate = ['-d', '-o', '-m', '--meta']
DATA_DIR = ""
OUTPUT_DIR = ""
MASK_DIR = ""
META_PATH = ""

def check_args(args: list):
    for arg in mandate:
        if not arg in args:
            raise ValueError(f"{arg} is a mandatory keyword, use -h for help")

def print_help():
    help_message = """
\033[1;36m
DRR Maker - Help
\033[0m
Usage:
  python drr_maker.py -d <data_directory> -m <mask_directory> -o <output_directory>

\033[1;33mOptions:\033[0m
  \033[1;32m-d\033[0m    Path to the directory containing full chest CT scans (.mhd)  \033[1;30m[Required]\033[0m
  \033[1;32m-m\033[0m    Path to the directory containing corresponding masks (.mhd)  \033[1;30m[Required]\033[0m
  \033[1;32m-o\033[0m    Output directory to store generated DRRs                 \033[1;30m[Required]\033[0m

\033[1;33mExample Usage:\033[0m
  \033[1;34mpython drr_maker.py -d /path/to/ct_scans -m /path/to/masks -o /path/to/output\033[0m

\033[1;35mDescription:\033[0m
  This script generates Digitally Reconstructed Radiographs (DRRs) from chest CT scans.
  It requires both the CT scan directory and the corresponding mask directory.
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
    global META_PATH
    DATA_DIR = args[args.index('-d')+1]
    OUTPUT_DIR = args[args.index('-o')+1]
    MASK_DIR = args[args.index('-m')+1]
    META_PATH = args[args.index('--meta')+1]

def start_patch():
    # data = {
    #     "data":DATA_DIR,
    #     "mask":MASK_DIR,
    #     "out": OUTPUT_DIR,
    # }
    process_ct_folder_drr(DATA_DIR, os.path.join(OUTPUT_DIR, "full_ct_xray"), META_PATH)
    process_seg_folder_drr(MASK_DIR, os.path.join(OUTPUT_DIR, "full_ct_mask"), META_PATH)
    # print("reached start patch")
    

def main(args: list):
    checks(args)
    set_vars(args)
    start_patch()