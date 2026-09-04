"""GPU environment detection and configuration guide."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.config import settings


def detect_gpu_environment():
    """Detect GPU environment and provide configuration guidance.
    
    Returns:
        Dictionary with GPU detection results and recommendations
    """
    result = {
        'cuda_available': False,
        'cuda_version': None,
        'gpu_name': None,
        'gpu_memory': None,
        'pytorch_available': False,
        'pytorch_version': None,
        'recommendations': []
    }
    
    # Check PyTorch availability
    try:
        import torch
        result['pytorch_available'] = True
        result['pytorch_version'] = torch.__version__
        
        # Check CUDA availability
        if torch.cuda.is_available():
            result['cuda_available'] = True
            result['cuda_version'] = torch.version.cuda
            result['gpu_count'] = torch.cuda.device_count()
            
            # Get GPU information
            for i in range(result['gpu_count']):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                
                result['gpu_name'] = gpu_name
                result['gpu_memory'] = gpu_memory
                
                result['recommendations'].append(
                    f"✅ GPU {i}: {gpu_name} ({gpu_memory:.2f} GB) detected"
                )
        else:
            result['recommendations'].append(
                "⚠️ CUDA not available, GPU acceleration will use CPU"
            )
            result['recommendations'].append(
                "💡 Install CUDA Toolkit: https://developer.nvidia.com/cuda-toolkit"
            )
            result['recommendations'].append(
                "💡 Install PyTorch with CUDA: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118"
            )
    except ImportError:
        result['pytorch_available'] = False
        result['recommendations'].append(
            "⚠️ PyTorch not installed"
        )
        result['recommendations'].append(
            "💡 Install PyTorch: pip install torch"
        )
    
    # Check sentence-transformers availability
    try:
        import sentence_transformers
        result['sentence_transformers_available'] = True
        result['recommendations'].append(
            "✅ sentence-transformers installed (required for GPU embedding)"
        )
    except ImportError:
        result['sentence_transformers_available'] = False
        result['recommendations'].append(
            "⚠️ sentence-transformers not installed (optional for GPU embedding)"
        )
        result['recommendations'].append(
            "💡 Install sentence-transformers: pip install sentence-transformers"
        )
    
    # Check current configuration
    result['current_config'] = {
        'embedding_device': settings.embedding_device,
        'embedding_batch_size': settings.embedding_batch_size,
        'enable_reranking': settings.enable_reranking,
        'reranking_device': settings.reranking_device,
        'reranking_batch_size': settings.reranking_batch_size
    }
    
    # Provide configuration recommendations
    if result['cuda_available']:
        if settings.embedding_device != 'cuda':
            result['recommendations'].append(
                "💡 Set embedding_device: cuda in config.py to enable GPU acceleration"
            )
        else:
            result['recommendations'].append(
                "✅ embedding_device is set to cuda"
            )
        
        if settings.enable_reranking and settings.reranking_device != 'cuda':
            result['recommendations'].append(
                "💡 Set reranking_device: cuda in config.py to enable GPU reranking"
            )
        elif settings.enable_reranking:
            result['recommendations'].append(
                "✅ reranking_device is set to cuda"
            )
    else:
        if settings.embedding_device == 'cuda':
            result['recommendations'].append(
                "⚠️ embedding_device is set to cuda but GPU not available"
            )
            result['recommendations'].append(
                "💡 Set embedding_device: cpu in config.py or install CUDA"
            )
        else:
            result['recommendations'].append(
                "✅ embedding_device is set to cpu (appropriate for current environment)"
            )
    
    return result


def print_gpu_detection_report():
    """Print GPU detection and configuration report."""
    
    print("=" * 60)
    print("GPU Environment Detection and Configuration")
    print("=" * 60)
    
    result = detect_gpu_environment()
    
    print("\nPyTorch Status:")
    print(f"  Available: {result['pytorch_available']}")
    if result['pytorch_available']:
        print(f"  Version: {result['pytorch_version']}")
    
    print("\nCUDA Status:")
    print(f"  Available: {result['cuda_available']}")
    if result['cuda_available']:
        print(f"  Version: {result['cuda_version']}")
        print(f"  GPU Count: {result['gpu_count']}")
        print(f"  GPU Name: {result['gpu_name']}")
        print(f"  GPU Memory: {result['gpu_memory']:.2f} GB" if result['gpu_memory'] else "N/A")
    
    print("\nsentence-transformers Status:")
    print(f"  Available: {result.get('sentence_transformers_available', False)}")
    
    print("\nCurrent Configuration:")
    config = result['current_config']
    print(f"  embedding_device: {config['embedding_device']}")
    print(f"  embedding_batch_size: {config['embedding_batch_size']}")
    print(f"  enable_reranking: {config['enable_reranking']}")
    print(f"  reranking_device: {config['reranking_device']}")
    print(f"  reranking_batch_size: {config['reranking_batch_size']}")
    
    print("\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  {rec}")
    
    print("\n" + "=" * 60)
    
    return result


if __name__ == "__main__":
    print_gpu_detection_report()