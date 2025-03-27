import subprocess
import sys
import os


args = sys.argv

if '-h' in args:
    print("""
\033[1;34mUsage:\033[0m script.py -d \033[1;32m<MAIN_DATA_DIR>\033[0m -o \033[1;32m<MAIN_OUTPUT_DIR>\033[0m -c \033[1;32m<CSV_PATH>\033[0m

\033[1;34mArguments:\033[0m
  \033[1;33m-d\033[0m    Path to the main data directory for a subset.
  \033[1;33m-o\033[0m    Path to the output directory where results will be stored.
  \033[1;33m-c\033[0m    Path to the annotations CSV file (\033[1;36mannotations.csv\033[0m) of the LUNA16 dataset.

\033[1;34mExample:\033[0m
  python script.py -d \033[1;32m/path/to/data\033[0m -o \033[1;32m/path/to/output\033[0m -c \033[1;32m/path/to/annotations.csv\033[0m
""")

    exit(0)

MAIN_DATA_DIR = args[args.index('-d')+1]
MAIN_OUTPUT_DIR = args[args.index('-o')+1]
CSV_PATH = args[args.index('-c')+1]
PATCH_MASK_DIR = os.path.join(MAIN_OUTPUT_DIR, 'patch_dataset')
INFERENCE_DIR = os.path.join(MAIN_OUTPUT_DIR, 'infered_dataset')
FULL_MASK_DIR = os.path.join(MAIN_OUTPUT_DIR, 'full_mask_dataset')
META_PATCH_DATASET_PATH = os.path.join(PATCH_MASK_DIR, 'meta.json')
META_FULL_MASK_PATH  = os.path.join(FULL_MASK_DIR, 'meta.json')
XRAY_DIR = os.path.join(MAIN_OUTPUT_DIR, 'xray_dataset')

paths = [PATCH_MASK_DIR, INFERENCE_DIR, FULL_MASK_DIR, XRAY_DIR, MAIN_OUTPUT_DIR]
for path in paths:
    os.makedirs(path, exist_ok=True)

extractor = f"python dataset_maker.py -d \"{MAIN_DATA_DIR}\" -o \"{PATCH_MASK_DIR}\" -c \"{CSV_PATH}\""
infer = f"python data_inference_vnet.py -i \"{PATCH_MASK_DIR}\" -o \"{INFERENCE_DIR}\""
patcher = f"python dataset_patcher.py -d \"{MAIN_DATA_DIR}\" -o \"{FULL_MASK_DIR}\" -r \"{INFERENCE_DIR}\" -m \"{META_PATCH_DATASET_PATH}\""
drrer = f"python drrer.py -d \"{MAIN_DATA_DIR}\" -m \"{FULL_MASK_DIR}\" -o \"{XRAY_DIR}\" --meta \"{META_FULL_MASK_PATH}\""

print("Starting Pipeline")
print("Starting Extraction")

process = subprocess.Popen(extractor)
process.wait()

print("Finished Extraction")
print("Starting Inference")

process = subprocess.Popen(infer)
process.wait()  

print("Finished Inference")
print("Starting Patching")

process = subprocess.Popen(patcher)
process.wait()

print("Finished Patching")
print("Starting DRR")

process = subprocess.Popen(drrer)
process.wait()  

print("Finished DRR")
print("Pipeline execution completed.")