import os
from utils.vinference import convert_to_vnet

mandate = ['-i', '-o']
DATA_DIR = ""
OUTPUT_DIR = ""

def check_args(args: list):
    for arg in mandate:
        if not arg in args:
            raise ValueError(f"{arg} is a mandatory keyword, use -h for help")

def print_help():
    help_message = """\033[1;36m
nnUNet CT Patch Inference - Help
\033[0m
Usage:
  python data_inference_nnunet.py -i <data_directory> -o <output_directory> 

\033[1;33mOptions:\033[0m
  \033[1;32m-d\033[0m    Path to the directory containing CT scans patches (.mhd)  \033[1;30m[Required]\033[0m
  \033[1;32m-o\033[0m    Output directory to store inferenced CT patches                \033[1;30m[Required]\033[0m

\033[1;33mExample Usage:\033[0m
  \033[1;34mdata_inference_nnunet.py -i /path/to/ct_scans -o /path/to/output\033[0m

\033[1;35mDescription:\033[0m
  This script runs an inference on 3d_fullres configuration of the nnUNet model using patches from chest CT scans stored in the specified directory.
  The 3D patch mask predicted by the nnUNET model will be stored in the specified output directory.
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
    DATA_DIR = args[args.index('-i')+1]
    OUTPUT_DIR = args[args.index('-o')+1]


def start_inf():
    data = {
        "data":DATA_DIR,
        "out": OUTPUT_DIR,
    }
    print(data)
    convert_to_vnet(data)
    

def main(args: list):
    checks(args)
    set_vars(args)
    start_inf()