import subprocess
import sys
import re

def get_cuda_version():
    """
    Detects the CUDA version installed on the system using nvidia-smi.
    Returns the appropriate PyTorch index URL for installation.
    """
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        match = re.search(r"CUDA Version: (\d+\.\d+)", result.stdout)
        if match:
            cuda_version = match.group(1)
            print(f"Detected CUDA Version: {cuda_version}")

            if cuda_version.startswith("12"):
                return "https://download.pytorch.org/whl/cu121"
            elif cuda_version.startswith("11"):
                return "https://download.pytorch.org/whl/cu118"
            else:
                print("Unsupported CUDA version detected! Installing CPU version.")
                return None  # Install CPU version
        else:
            print("CUDA not found! Installing CPU version.")
            return None  # Install CPU version
    except FileNotFoundError:
        print("nvidia-smi not found! Installing CPU version.")
        return None  # Install CPU version

def install_pytorch():
    """
    Installs the correct PyTorch version based on detected CUDA.
    """
    index_url = get_cuda_version()
    package_list = ["torch", "torchvision", "torchaudio"]

    try:
        if index_url:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *package_list, "--index-url", index_url])
        else:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *package_list])
        
        print("PyTorch installation complete!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing PyTorch: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_pytorch()