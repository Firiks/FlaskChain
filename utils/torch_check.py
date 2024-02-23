"""
Test torch and torchvision versions
"""

def get_versions():
    import torch
    print('torch ', torch.__version__)

    import torchvision
    print('torchvision ', torchvision.__version__)

if __name__ == "__main__":
    get_versions()