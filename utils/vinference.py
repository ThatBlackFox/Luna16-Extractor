import os
import glob
import torch
import SimpleITK as sitk
import numpy as np
from tqdm import tqdm
import torch.nn as nn
import torch.nn.functional as F
 

# Define ResidualBlock and VNet classes (unchanged from your provided code)
class ResidualBlock(nn.Module):
    def __init__(self, in_c, out_c):
        super().__init__()
        self.conv1 = nn.Conv3d(in_c, out_c, 3, padding=1)
        self.norm1 = nn.InstanceNorm3d(out_c)
        self.conv2 = nn.Conv3d(out_c, out_c, 3, padding=1)
        self.norm2 = nn.InstanceNorm3d(out_c)
        self.shortcut = nn.Sequential(
            nn.Conv3d(in_c, out_c, 1),
            nn.InstanceNorm3d(out_c)
        ) if in_c != out_c else nn.Identity()

    def forward(self, x):
        residual = self.shortcut(x)
        x = F.relu(self.norm1(self.conv1(x)))
        x = self.norm2(self.conv2(x))
        return F.relu(x + residual)


class VNet(nn.Module):
    def __init__(self, in_channels=1, out_channels=1):
        super(VNet, self).__init__()

        # Encoder
        self.enc1 = ResidualBlock(in_channels, 64)
        self.pool1 = nn.MaxPool3d(2)
        self.enc2 = ResidualBlock(64, 128)
        self.pool2 = nn.MaxPool3d(2)
        self.enc3 = ResidualBlock(128, 256)
        self.pool3 = nn.MaxPool3d(2)

        # Bottleneck
        self.bottleneck = nn.Sequential(
            ResidualBlock(256, 512),
            nn.Dropout3d(0.5)
        )

        # Decoder
        self.up3 = nn.ConvTranspose3d(512, 256, 2, stride=2)
        self.dec3 = ResidualBlock(512, 256)
        self.up2 = nn.ConvTranspose3d(256, 128, 2, stride=2)
        self.dec2 = ResidualBlock(256, 128)
        self.up1 = nn.ConvTranspose3d(128, 64, 2, stride=2)
        self.dec1 = ResidualBlock(128, 64)

        # Output
        self.final = nn.Conv3d(64, out_channels, 1)

        # Attention Modules
        self.attention3 = nn.Sequential(
            nn.Conv3d(256, 1, kernel_size=1),
            nn.Sigmoid()
        )
        self.attention2 = nn.Sequential(
            nn.Conv3d(128, 1, kernel_size=1),
            nn.Sigmoid()
        )
        self.attention1 = nn.Sequential(
            nn.Conv3d(64, 1, kernel_size=1),
            nn.Sigmoid()
        )       

    def forward(self, x):
        # Encoder
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool1(e1))
        e3 = self.enc3(self.pool2(e2))

        # Bottleneck
        b = self.bottleneck(self.pool3(e3))

        # Decoder with Attention
        d3 = self.up3(b)
        if d3.size()[2:] != e3.size()[2:]:
            d3 = F.interpolate(d3, size=e3.size()[2:], mode='trilinear', align_corners=False)
        
        att3 = self.attention3(e3)
        e3 = e3 * att3
        d3 = torch.cat([d3, e3], dim=1)
        d3 = self.dec3(d3)

        d2 = self.up2(d3)
        if d2.size()[2:] != e2.size()[2:]:
            d2 = F.interpolate(d2, size=e2.size()[2:], mode='trilinear', align_corners=False)
        
        att2 = self.attention2(e2)
        e2 = e2 * att2
        d2 = torch.cat([d2, e2], dim=1)
        d2 = self.dec2(d2)

        d1 = self.up1(d2)
        if d1.size()[2:] != e1.size()[2:]:
            d1 = F.interpolate(d1, size=e1.size()[2:], mode='trilinear', align_corners=False)
        
        att1 = self.attention1(e1)
        e1 = e1 * att1
        d1 = torch.cat([d1, e1], dim=1)
        d1 = self.dec1(d1)
        return self.final(d1)




def convert_to_vnet(data: dict):
    """
    Loads MHD images and runs VNet segmentation directly on them.
    """
    INPUT = data['data']
    OUTPUT = data['out']

    
    ct_patches = sorted(glob.glob(os.path.join(INPUT, "*.mhd")))
    print(f"🔍 Found {len(ct_patches)} MHD files.")

    vnet_inference(INPUT, OUTPUT)
    print(f"✅ Segmentation completed for {len(ct_patches)} images.")


def vnet_inference(input_folder, output_folder):
    torch.cuda.init()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    try:
        model = VNet(in_channels=1, out_channels=1).to(device)
        weight_path = "./weights/best_model1.pth"
        if not os.path.exists(weight_path):
            raise FileNotFoundError(f"Weight file not found: {weight_path}")
        
        model.load_state_dict(torch.load(weight_path, map_location=device), strict=False)
        model.eval()
    except Exception as e:
        print(f"⚠️ Model loading error: {e}")
        return

    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(input_folder):
        if not filename.endswith(".mhd"):
            continue
            
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        try:
          
            image = sitk.ReadImage(input_path)
            array = sitk.GetArrayFromImage(image).astype(np.float32)
            print(f"Processing: {filename} | Shape: {array.shape}")
            
           
                
          
            array = (array - array.min()) / (array.max() - array.min() + 1e-8)
            tensor = torch.tensor(array).unsqueeze(0).unsqueeze(0).to(device)
            print(f"Input tensor shape: {tensor.shape}")
            
     
            with torch.no_grad():
                output = model(tensor)
                output = torch.sigmoid(output)
                output = (output > 0.5).float()
            
            
            output_array = output.squeeze().cpu().numpy()
            output_image = sitk.GetImageFromArray(output_array)
            output_image.CopyInformation(image)
            sitk.WriteImage(output_image, output_path)
            print(f"✅ Saved: {output_path}")
            
        except Exception as e:
            print(f"⚠️ Error processing {filename}: {e}")