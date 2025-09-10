import torch

def test_pytorch_setup():
    print("---- PyTorch Environment Check ----")
    
    print(f"PyTorch version: {torch.__version__}")

    print(f"Built with CUDA: {torch.version.cuda is not None}")
    print(f"CUDA version (PyTorch): {torch.version.cuda}")

    gpu_available = torch.cuda.is_available()
    print(f"CUDA available (GPU detected): {gpu_available}")

    if gpu_available:
        num_devices = torch.cuda.device_count()
        print(f"Number of GPUs detected: {num_devices}")
        for i in range(num_devices):
            print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
            print(f"    Memory Allocated: {torch.cuda.memory_allocated(i)/1024**2:.2f} MB")
            print(f"    Memory Cached: {torch.cuda.memory_reserved(i)/1024**2:.2f} MB")
    else:
        print("No GPU detected. Running on CPU.")

if __name__ == "__main__":
    test_pytorch_setup()
