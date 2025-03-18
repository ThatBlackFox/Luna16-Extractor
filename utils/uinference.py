import os
import glob
import SimpleITK as sitk
import json
import shutil
import numpy as np
from tqdm import tqdm
import os
import subprocess
import nibabel as nib

INF_IN=""
INF_OUT=""

def convert_to_nnunet(data:dict): #converts .mhd dataset into nifti files as required by nnunet for inference
    # Set paths
    INPUT=data['data']
    OUTPUT=data['out']
    global INF_IN
    global INF_OUT
    ufdata = INPUT  
    fdata = os.path.join(ufdata, "nifti")
    os.makedirs(fdata, exist_ok=True)
    ct_patches = sorted(glob.glob(os.path.join(ufdata, "*.mhd")))
    for i, ct_path in tqdm(enumerate(ct_patches), total=len(ct_patches)):
        ct_image = sitk.ReadImage(ct_path)
        ct_array = sitk.GetArrayFromImage(ct_image).astype(np.float32)
        back="\\"
        ct_nifti_path = os.path.join(fdata, f"{ct_path.split(back)[-1][:-4]}_0000.nii.gz")  # "_0000" for modality 0
        try:
            sitk.WriteImage(sitk.GetImageFromArray(ct_array), ct_nifti_path)
            print(f"✅ Saved {ct_nifti_path}")
        except Exception as e:
            print(f"❌ Error saving {ct_nifti_path}: {e}")

    print(f"✅ Converted {len(ct_patches)} training samples.")
    INF_IN=fdata
    INF_OUT=OUTPUT
    nnunet_inference()

def nnunet_inference():
    """
    Runs inference using nnUNet's 3D full resolution configuration.
    """
    command = [
        "nnUNetv2_predict",
        "-i", INF_IN,
        "-o", INF_OUT,
        "-d", "Dataset501_Node21",  # Replace with the actual dataset ID used for training
        "-c", "3d_fullres",
    ]
    os.environ["nnUNet_raw"] = r"E:\NITK Datasets\nnUNet_raw_data"
    os.environ["nnUNet_results"] = r"E:\NITK Datasets\nnUNet_results"
    os.environ["nnUNet_preprocessed"] = r"E:\NITK Datasets\nnUNet_preprocessed"

    # Verify they are set
    print("Environment Variables Set:")
    for var in ["nnUNet_raw", "nnUNet_results", "nnUNet_preprocessed"]:
        print(f"{var} = {os.environ[var]}")

    try:
        print("\nRunning nnUNet Inference...")
        subprocess.run(command, check=True,env=os.environ)
        print("Inference completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error during inference: {e}")

