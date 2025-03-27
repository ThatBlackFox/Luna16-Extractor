import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt
import cv2
import json
from scipy.ndimage import map_coordinates
import os
import torch
import torch.nn.functional as F

def load_mhd_image(mhd_path):
    """
    Load MHD Image
    
    Args:
        mhd_path (str): Path to the MHD file
    
    Returns:
        SimpleITK Image object
    """
    image = sitk.ReadImage(mhd_path)
    return image

def resample_image(image, new_spacing=[1.0, 1.0, 1.0]):
    """
    Resample Image Data to Ensure Isotropic Voxel Spacing
    
    Args:
        image (SimpleITK Image): Input image
        new_spacing (list): Desired voxel spacing
    
    Returns:
        Resampled SimpleITK Image
    """
    spacing = image.GetSpacing()
    size = image.GetSize()
    new_size = [int(size[i] * (spacing[i] / new_spacing[i])) for i in range(3)]
   
    resampler = sitk.ResampleImageFilter()
    resampler.SetOutputSpacing(new_spacing)
    resampler.SetSize(new_size)
    resampler.SetOutputDirection(image.GetDirection())
    resampler.SetOutputOrigin(image.GetOrigin())
    resampler.SetInterpolator(sitk.sitkLinear)
    return resampler.Execute(image)

def enhance_contrast(drr):
    """Apply CLAHE to enhance small structures in the DRR."""

    drr_uint8 = (drr * 255).astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16, 16))
    enhanced_drr = clahe.apply(drr_uint8)

    return enhanced_drr / 255.0 

def generate_drr(ct_array, projection_axis=0, output_size=(512, 512)):
    """Generate a DRR and normalize values between 0 and 1."""
    drr = np.max(ct_array, axis=projection_axis)
    
    drr = (drr - np.min(drr)) / (np.max(drr) - np.min(drr))

    drr_uint8 = (drr * 255).astype(np.uint8)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_drr = clahe.apply(drr_uint8)

    resized_drr = cv2.resize(enhanced_drr, output_size, interpolation=cv2.INTER_AREA)
    resized_drr = np.flipud(resized_drr)

    print(f"DRR shape: {resized_drr.shape}, min: {np.min(resized_drr):.2f}, max: {np.max(resized_drr):.2f}")
    
    
    return resized_drr


def raycast(image, detector_size=(512, 512), source_to_detector_distance=1300):
  
    np_image = sitk.GetArrayFromImage(image) 
    np_image = np.clip(np_image, -600, 100) 
    np_image = (np_image - np.min(np_image)) / (np.max(np_image) - np.min(np_image))  

   
    tensor_image = torch.tensor(np_image, dtype=torch.float32, device="cuda").unsqueeze(0).unsqueeze(0)

    
    depth, height, width = np_image.shape
    z_coords = torch.linspace(0, depth - 1, detector_size[0], device="cuda")
    x_coords = torch.linspace(0, width - 1, detector_size[1], device="cuda")
    zz, xx = torch.meshgrid(z_coords, x_coords, indexing="ij")

  
    zz = zz / (depth - 1) * 2 - 1  
    xx = xx / (width - 1) * 2 - 1

    
    grid = torch.stack((xx, zz), dim=-1).unsqueeze(0)  

    
    drr = torch.zeros(detector_size, dtype=torch.float32, device="cuda")

   
    for y in range(height):
        slice_2d = tensor_image[:, :, :, y, :]  

        
        interp_values = F.grid_sample(slice_2d, grid, align_corners=True, mode="bilinear")

        drr += interp_values.squeeze() 

    drr = drr / height  
    drr = torch.exp(-drr / source_to_detector_distance)  


    drr = (drr - torch.min(drr)) / (torch.max(drr) - torch.min(drr) + 1e-6)

    drr = 1.0 - drr
    drr=drr.cpu().numpy() 
    drr = enhance_contrast(drr)
    drr = np.flipud(drr)

    print(f"DRR shape: {drr.shape}, min: {np.min(drr):.2f}, max: {np.max(drr):.2f}")
    return drr

def save_drr_image(drr, output_path):
    """Save DRR as an image."""
    plt.imsave(output_path, drr, cmap='gray')



def process_mhd_folder_raycast(folder_path, output_dir, meta_path):
    """Process all MHD files in the given folder except those listed in meta.json."""

    excluded_files = set()
    if os.path.exists(meta_path):
        with open(meta_path, "r") as meta_file:
            meta_data = json.load(meta_file)
            excluded_files = set(meta_data.keys()) 
        
        os.makedirs(output_dir, exist_ok=True)

        for file in os.listdir(folder_path):
            if file.endswith(".mhd") and '.'.join(file.split('.')[:-1]) not in excluded_files:
                file_path = os.path.join(folder_path, file)
                print(f"Processing: {file}")

                ct_image = load_mhd_image(file_path)
                resampled_image = resample_image(ct_image)
                
                drr_image = raycast(resampled_image)

                output_path = os.path.join(output_dir, f"{file[:-4]}.png")
                save_drr_image(drr_image, output_path)

        print("Processing complete. DRR images saved in:", output_dir)

def process_mhd_folder_max(folder_path, output_dir, meta_path):
    """Process all MHD files in the given folder except those listed in meta.json."""

    excluded_files = set()
    if os.path.exists(meta_path):
        with open(meta_path, "r") as meta_file:
            meta_data = json.load(meta_file)
            excluded_files = set(meta_data.keys()) 
        
        os.makedirs(output_dir, exist_ok=True)
    
        for file in os.listdir(folder_path):

            if file.endswith(".mhd") and '.'.join(file.split('.')[:-2]) not in excluded_files:
                file_path = os.path.join(folder_path, file)
                print(f"Processing: {file}")

                ct_image = load_mhd_image(file_path)
                resampled_image = resample_image(ct_image)
                resample_array = sitk.GetArrayFromImage(resampled_image)
                
                drr_image = generate_drr(resample_array, 1)

                output_path = os.path.join(output_dir, f"{file[:-8]}.png")
                save_drr_image(drr_image, output_path)

        print("Processing complete. DRR images saved in:", output_dir)