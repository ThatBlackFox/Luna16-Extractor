import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt
import cv2
import json
from scipy.ndimage import map_coordinates
import os


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
    drr_uint8 = (drr * 255).astype(np.uint8)  # Convert to 8-bit image
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16, 16))
    enhanced_drr = clahe.apply(drr_uint8)  # Apply CLAHE
    return enhanced_drr / 255.0  # Convert back to [0,1] range

def generate_drr(ct_array, projection_axis=0, output_size=(512, 512)):
    """Generate a DRR and normalize values between 0 and 1."""
    drr = np.max(ct_array, axis=projection_axis)  # Average Intensity Projection (AIP)
    
    # Normalize to 0-1 range
    drr = (drr - np.min(drr)) / (np.max(drr) - np.min(drr))

    # Convert to 8-bit for visualization (0-255)
    drr_uint8 = (drr * 255).astype(np.uint8)

    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_drr = clahe.apply(drr_uint8)

    # Resize to a fixed output size
    resized_drr = cv2.resize(enhanced_drr, output_size, interpolation=cv2.INTER_AREA)
    resized_drr = np.flipud(resized_drr)

    print(f"DRR shape: {resized_drr.shape}, min: {np.min(resized_drr):.2f}, max: {np.max(resized_drr):.2f}")
    
    
    return resized_drr  # Returns an 8-bit image (0-255)


def raycast(image, detector_size=(512, 512), source_to_detector_distance=1300):
    """
    Generate a coronal DRR using ray-casting with numerical stability fixes.
    """
    np_image = sitk.GetArrayFromImage(image)  # Shape (Z, Y, X)
    depth, height, width = np_image.shape

    
    np_image = np.clip(np_image, a_min=-600, a_max=100)  # Keep relevant HU range
    np_image = np_image = (np_image - np.min(np_image)) / (np.max(np_image) - np.min(np_image))  # Scale to [0, 1]

   
    drr = np.zeros(detector_size, dtype=np.float32)

    
    z_coords = np.linspace(0, depth - 1, detector_size[0])
    x_coords = np.linspace(0, width - 1, detector_size[1])
    zz, xx = np.meshgrid(z_coords, x_coords, indexing="ij")

    
    for y in range(height):
        slice_2d = np_image[:, y, :]
        interp_values = map_coordinates(slice_2d, [zz, xx], order=3)
        drr += interp_values

    drr = drr / height  
    drr = np.exp(-drr / source_to_detector_distance)

    drr = np.nan_to_num(drr, nan=0.0, posinf=0.0, neginf=0.0)

    if np.ptp(drr) > 0:
        drr = (drr - np.min(drr)) / np.ptp(drr)
    else:
        drr = np.zeros_like(drr)

    
    drr = 1.0 - drr  

    
    drr = enhance_contrast(drr)

   
    drr = np.flipud(drr)

    print(f"DRR shape: {drr.shape}, min: {np.min(drr):.2f}, max: {np.max(drr):.2f}")
    return drr

def save_drr_image(drr, output_path):
    """Save DRR as an image."""
    plt.imsave(output_path, drr, cmap='gray')



def process_mhd_folder_raycast(folder_path, output_dir, meta_path):
    """Process all MHD files in the given folder except those listed in meta.json."""
    # meta_path = os.path.join(folder_path)
    # meta_path =  "meta.json"

    excluded_files = set()
    if os.path.exists(meta_path):
        with open(meta_path, "r") as meta_file:
            meta_data = json.load(meta_file)
            excluded_files = set(meta_data.keys()) 
        
        # output_dir = os.path.join(folder_path, "drr_outputs")
        os.makedirs(output_dir, exist_ok=True)

    
        for file in os.listdir(folder_path):
            if file.endswith(".mhd") and file not in excluded_files:
                file_path = os.path.join(folder_path, file)
                print(f"Processing: {file}")

                ct_image = load_mhd_image(file_path)
                resampled_image = resample_image(ct_image)
                
                drr_image = raycast(resampled_image)

                output_path = os.path.join(output_dir, f"{file}.png")
                save_drr_image(drr_image, output_path)

        print("Processing complete. DRR images saved in:", output_dir)

def process_mhd_folder_max(folder_path, output_dir, meta_path):
    """Process all MHD files in the given folder except those listed in meta.json."""
    # meta_path = os.path.join(folder_path)

    # meta_path =  "meta.json"

    excluded_files = set()
    if os.path.exists(meta_path):
        with open(meta_path, "r") as meta_file:
            meta_data = json.load(meta_file)
            excluded_files = set(meta_data.keys()) 
        
        # output_dir = os.path.join(folder_path, "drr_outputs")
        os.makedirs(output_dir, exist_ok=True)

    
        for file in os.listdir(folder_path):
            if file.endswith(".mhd") and file[:-4] not in excluded_files:
                file_path = os.path.join(folder_path, file)
                print(f"Processing: {file}")

                
                ct_image = load_mhd_image(file_path)
                resampled_image = resample_image(ct_image)
                resample_array = sitk.GetArrayFromImage(resampled_image)

                
                drr_image = generate_drr(resample_array, 1)

                
                output_path = os.path.join(output_dir, f"{file}.png")
                save_drr_image(drr_image, output_path)

        print("Processing complete. DRR images saved in:", output_dir)