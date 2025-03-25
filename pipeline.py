import subprocess
import sys
import os


args = sys.argv
MAIN_DATA_DIR = args[args.index('-d')+1]
MAIN_OUTPUT_DIR = args[args.index('-o')+1]
CSV_PATH = args[args.index('-c')+1]
PATCH_MASK_DIR = os.path.join(MAIN_OUTPUT_DIR, 'patch_dataset')
INFERENCE_DIR = os.path.join(MAIN_OUTPUT_DIR, 'infered_dataset')
FULL_MASK_DIR = os.path.join(MAIN_OUTPUT_DIR, 'full_mask_dataset')
META_PATH = os.path.join(PATCH_MASK_DIR, 'meta.json')
XRAY_PATH = os.path.join(MAIN_OUTPUT_DIR, 'xray_dataset')

extractor = f"python dataset_maker.py -d {MAIN_DATA_DIR} -o {PATCH_MASK_DIR} -c {CSV_PATH}"
infer = f"python dataset_maker.py -d {PATCH_MASK_DIR} -o {INFERENCE_DIR}"
patcher = f"python dataset_patcher.py -d {MAIN_DATA_DIR} -o {FULL_MASK_DIR} -r {INFERENCE_DIR} -m {META_PATH}"
drrer = f"python drrer.py -d {MAIN_DATA_DIR} -m {FULL_MASK_DIR} -o {XRAY_PATH} --meta {META_PATH}"

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



