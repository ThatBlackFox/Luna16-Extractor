import SimpleITK as sitk
import os

def extract_cube(mhd_file, world_coord, cube_size):
    """
    Extracts a cube region around a given world coordinate from an MHD file.
    
    Parameters:
      mhd_file   : str, path to the .mhd file.
      world_coord: tuple, (x, y, z) world coordinate.
      cube_size  : tuple, (cube_width, cube_height, cube_depth).
                   (ITK uses (x, y, z) order; for a shallow cube, cube_depth is small)
    
    Returns:
      extracted_cube: SimpleITK.Image, the extracted region (binary mask expected).
      start_index   : list of ints, the (x, y, z) index where the extraction starts.
      extract_size  : list of ints, the actual size used (may be smaller near image borders).
    """
    image = sitk.ReadImage(mhd_file)
    img_size = image.GetSize()  # (x, y, z)
    
    index = image.TransformPhysicalPointToIndex(world_coord)
    
    cube_width, cube_height, cube_depth = cube_size
    
    start_index = [
        max(index[0] - cube_width // 2, 0),
        max(index[1] - cube_height // 2, 0),
        max(index[2] - cube_depth // 2, 0)
    ]
    
    end_index = [
        min(start_index[0] + cube_width, img_size[0]),
        min(start_index[1] + cube_height, img_size[1]),
        min(start_index[2] + cube_depth, img_size[2])
    ]
    
    extract_size = [end_index[i] - start_index[i] for i in range(3)]
    
    extractor = sitk.RegionOfInterestImageFilter()
    extractor.SetIndex(start_index)
    extractor.SetSize(extract_size)
    extracted_cube = extractor.Execute(image)
    
    return extracted_cube, start_index, extract_size

def patch_cube(original_image, cube, start_index, output_file):
    """
    Creates a new image with a white (255) background and pastes the binary mask into its
    original location. The binary mask is assumed to contain values 0 and 1; it is inverted
    so that the foreground (mask==1) appears black (0) and the background (mask==0) remains white.
    
    Parameters:
      original_image: SimpleITK.Image, the original image (used for dimensions/metadata).
      cube: SimpleITK.Image, the extracted cube (binary mask expected).
      start_index   : list of ints, the (x, y, z) index where the mask was extracted.
      output_file   : str, path to save the modified image.
    """

    orig_array = sitk.GetArrayFromImage(original_image)
    cube_array = sitk.GetArrayFromImage(cube)
    
    cube_depth, cube_height, cube_width = cube_array.shape
    
    x_start, y_start, z_start = start_index
    z_end = z_start + cube_depth
    y_end = y_start + cube_height
    x_end = x_start + cube_width
    
    orig_array[z_start:z_end, y_start:y_end, x_start:x_end] = cube_array
    
    result_image = sitk.GetImageFromArray(orig_array)
    result_image.CopyInformation(original_image)
    
    sitk.WriteImage(result_image, output_file)

def load_image(path: os.PathLike):
    return sitk.ReadImage(path)

# ----- Example Usage -----
if __name__ == "__main__":
    mhd_path = "D:\\subset_0 Sample\\1.3.6.1.4.1.14519.5.2.1.6279.6001.141069661700670042960678408762.mhd"
    world_point = (-101.9672788, 248.736321, -739.8746836)  # Example world coordinate
    cube_dimensions = (50, 50, 50)  # Width, Depth, Shallow Height
    output_mhd = "modified2.mhd"                   # Output file path.

    extracted_cube, start_idx, extract_sz = extract_cube(mhd_path, world_point, cube_dimensions)

    original_img = sitk.ReadImage(mhd_path)

    patch_cube(original_img, extracted_cube, start_idx, output_mhd)