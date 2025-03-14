import utils.image_handler as image_handler
import SimpleITK as sitk
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
import json

def extracting(data: dict):
    print(data)
    DATA_DIR = data['data']
    CSV_PATH = data['csv']
    OUTPUT_PATH = data['out']
    annots = pd.read_csv(CSV_PATH)
    files = [file for file in os.listdir(DATA_DIR) if file[-4:] == '.mhd']
    cube_dimensions = (50, 50, 50)
    meta_data = {}
    for file in tqdm(files):
        coord_rows = annots[annots['seriesuid']==file[:-4]]

        for index, row in enumerate(coord_rows.iterrows()):
            x,y,z = row[1][1:4]

            patch, start_index, extract_size = image_handler.extract_cube(
                os.path.join(DATA_DIR, file),
                (x, y, z),
                cube_dimensions
                )
            path = os.path.join(OUTPUT_PATH, file[:-4]+"_"+str(index)+".mhd")
            
            try:
                sitk.WriteImage(patch, path)
                meta_data[file[:-4]+"_"+str(index)] = {"start_index": start_index, "extract_size": extract_size}
            except RuntimeError as e:
                print(f"{file} - {index}: One patch failed")
                print(e)
    with open(os.path.join(OUTPUT_PATH, "meta.json"), 'w') as f:
        json.dump(meta_data, f)

def patching(data: dict):
    print(data)
    DATA_DIR = data['data']
    META_PATH = data['meta']
    OUTPUT_DIR = data['out']
    REF_DIR = data['ref']

    with open(META_PATH, 'r') as f:
        meta = json.load(f)
    
    parent_files = [file for file in os.listdir(DATA_DIR) if file[-4:] == '.mhd']
    seg_files = [file for file in os.listdir(REF_DIR) if file[-4:] == '.mhd']
    for parent in tqdm(parent_files):

        parent_image = sitk.ReadImage(os.path.join(DATA_DIR, parent))
        blank_array = np.zeros_like(sitk.GetArrayFromImage(parent_image))
        blank_image = sitk.GetImageFromArray(blank_array)
        blank_image.CopyInformation(parent_image)

        for child in seg_files:
            if parent[:-4] not in child:
                continue
            cube = sitk.ReadImage(os.path.join(REF_DIR, child))
            start_index = meta[child[:-4]]['start_index']
            blank_image = image_handler.patch_cube(blank_image, cube, start_index)
        
        out_path = os.path.join(OUTPUT_DIR, parent)
        sitk.WriteImage(blank_image, f"{out_path}_seg.mhd")

