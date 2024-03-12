"""
Test torch and torchvision versions
"""
import torch
import torchvision
from torch import cuda

def get_versions():
    print('torch ', torch.__version__)

    print('torchvision ', torchvision.__version__)

    print('cuda current device ', cuda.current_device())

if __name__ == "__main__":
    get_versions()