import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
import cv2
import os
import json

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

def load_ct_image(file_path):
    """Load CT image from a DICOM/NIfTI file."""
    image = sitk.ReadImage(file_path)
    # print("reached load ct")
    resampled_image=resample_image(image)
    resampled_array = sitk.GetArrayFromImage(resampled_image)  # Convert to NumPy array
    # print(array.shape)
    return resampled_array

def save_drr_image(drr, output_path):
    """Save DRR as an image."""
    plt.imsave(output_path, drr, cmap='gray')
    
def generate_drr(ct_array, projection_axis=1):
    """Generate a simple DRR using Average Intensity Projection (AIP)."""
    drr = np.mean(ct_array, axis=projection_axis)  # Projection along slices
    drr = (drr - np.min(drr)) / (np.max(drr) - np.min(drr)) * 255
    drr = drr.astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_drr = clahe.apply(drr)
    # return enhanced_image
    return enhanced_drr

def generate_drr_mask(ct_array, projection_axis=1):
    """Generate a simple DRR using Maximum Intensity Projection for the mask (MIP)."""
    drr = np.max(ct_array, axis=projection_axis)  # Projection along slices
    drr = (drr - np.min(drr)) / (np.max(drr) - np.min(drr)) * 255
    drr = drr.astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_drr = clahe.apply(drr)
    # return enhanced_image
    return enhanced_drr

# def plot_drr(drr_image, original_shape, title):
#     """Display the DRR image with corrected aspect ratio."""
    
#     coronal_height, coronal_width = drr_image.shape  # Extract dimensions
#     orig_height, orig_width = original_shape  # Original CT shape (height, width)
    
#     # Calculate aspect ratio
#     aspect_ratio = orig_width / orig_height  # Maintain proportions
    
#     # Resize the DRR to match the original aspect ratio
#     new_width = int(coronal_height * aspect_ratio)  # Adjust width to match ratio
#     resized_drr = cv2.resize(drr_image, (new_width, coronal_height), interpolation=cv2.INTER_LINEAR)
    
#     # Plot with corrected aspect ratio
#     # plt.figure(figsize=(10, 10 * (coronal_height / new_width)))  # Dynamic figsize
#     plt.imshow(resized_drr, cmap='gray', origin='lower')
#     plt.title(title)
#     plt.axis('off')
#     plt.show()
    
def process_ct_folder_drr(folder_path, output_dir, meta_path):
    """Process all MHD files in the given folder except those listed in meta.json."""
    # meta_path = os.path.join(folder_path)

    # meta_path =  "meta.json"  
    # print("reached process ct")
    excluded_files = set()
    if os.path.exists(meta_path):
        with open(meta_path, "r") as meta_file:
            meta_data = json.load(meta_file)
            excluded_files = set(meta_data.keys()) 
        
        # output_dir = os.path.join(folder_path, "drr_outputs")
        os.makedirs(output_dir, exist_ok=True)

    
        for file in os.listdir(folder_path):
            if file.endswith(".mhd") and file in excluded_files:
                continue
            # if file.endswith(".mhd") and file[:-8] not in excluded_files:
            elif file.endswith(".mhd") :
                file_path = os.path.join(folder_path, file)
                print(f"Processing: {file}")

                
                resampled_array = load_ct_image(file_path)
                # resampled_image = resample_image(ct_image)

                
                drr_image = np.flipud(generate_drr(resampled_array,1))

                
                output_path = os.path.join(output_dir, f"{file}.png")
                save_drr_image(drr_image, output_path)

        print("Processing complete. DRR images saved in:", output_dir)
        
def process_seg_folder_drr(folder_path, output_dir, meta_path):
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
            # if file[:-8] in excluded_files:
            #     print(f"{file[:-8]} found in excluded files json file")
            if file.endswith(".mhd") and file in excluded_files:
                continue
            # if file.endswith(".mhd") and file[:-8] not in excluded_files:
            elif file.endswith(".mhd") :
                # print(file[:-8])
                file_path = os.path.join(folder_path, file)
                print(f"Processing: {file}")

                resampled_array = load_ct_image(file_path)
                # resampled_image = resample_image(ct_image)
                # resample_array = sitk.GetArrayFromImage(resampled_image)

                
                drr_image = np.flipud(generate_drr_mask(resampled_array, 1))

                
                output_path = os.path.join(output_dir, f"{file}.png")
                save_drr_image(drr_image, output_path)

        print("Processing complete. DRR images saved in:", output_dir)
# ct_dir=r"E:\NITK Datasets\subset0_LUNA16"
# mask_dir=r"E:\NITK Datasets\subset0_seg_LUNA16"
# with open(r"E:\NITK Datasets\subset0_seg_LUNA16\meta.json", 'r') as file:
#     json = json.load(file)
# # json=json.loads(r"E:\NITK Datasets\subset0_seg_LUNA16\meta.json")
# ct_files=[file for file in os.listdir(ct_dir) if file[-4:]==".mhd"]
# mask_files=[file for file in os.listdir(mask_dir) if file[-4:]==".mhd"]
# # print(json)
# for i,j in zip(ct_files,mask_files):
#     if i in json:
#         continue
#     else:
#         ct_array, ct_image = load_ct_image(os.path.join(ct_dir,i))
#         mask_array,mask_image=load_ct_image(os.path.join(mask_dir,j))

#     # Extract original shape (Height, Width) of a single slice
#     original_shape_ct = ct_array.shape[1:]  # (Height, Width)
#     original_shape_mask=mask_array.shape[1:]

#     # Generate coronal projection (Collapse along axis 1)
#     drr_image_ct = generate_drr(ct_array, projection_axis=1)   
#     plot_drr(drr_image_ct, original_shape_ct,i)
#     drr_image_mask=generate_drr_mask(mask_array,projection_axis=1)
#     plot_drr(drr_image_mask,original_shape_mask,j)
