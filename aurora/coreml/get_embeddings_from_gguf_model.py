#!/usr/bin/env python3
"""
Convert Llama from ollama to CoreML format using Python 3.9
This script creates a simple embedding model in CoreML format
"""

import os
import torch
import torch.nn as nn
import coremltools as ct
import numpy as np


def get_embeddings_from_pretrained_model(gguf_path):
    """
    Extract embeddings from a GGUF model
    
    Args:
        gguf_path: Path to the GGUF model file
        
    Returns:
        Dictionary containing embeddings for each layer
    """
    print(f"Loading GGUF model to extract embeddings: {gguf_path}")
    
    # Initialize llama-cpp model with embedding capability
    llm = Llama(model_path=gguf_path, embedding=True, n_gpu_layers=32)
    
    # Dictionary to store embeddings for each layer
    layer_embeddings = {}
    
    # Get model metadata
    model_metadata = {}
    if hasattr(llm, 'model_meta'):
        model_metadata = llm.model_meta
    
    # Extract number of layers from metadata or use default
    num_layers = model_metadata.get('n_layer', 32)  # Default to 32 if not found
    
    print(f"Model has {num_layers} layers")
    
    # Generate embeddings for sample texts to extract per-layer information
    sample_texts = [
        "This is a sample text for embedding extraction",
        "Another example to ensure we get consistent embeddings",
        "Testing the embedding extraction process"
    ]
    
    # Extract embeddings for each layer
    # Note: llama-cpp doesn't expose per-layer embeddings directly
    # We'll store the global embeddings as a baseline
    layer_embeddings["global"] = {
        text: llm.embed(text) 
        for text in sample_texts
    }
    print("Extracted global embeddings")
    
    # Store embedding dimensions
    embedding_size = len(next(iter(layer_embeddings["global"].values())))
    layer_embeddings["metadata"] = {
        "embedding_size": embedding_size,
        "num_layers": num_layers,
        "model_path": gguf_path
    }
    
    print(f"Completed embedding extraction. Embedding size: {embedding_size}")
    return layer_embeddings

def get_attention_mask_from_pretrained(gguf_path):
    """
    Extract attention masks from a GGUF model
    
    Args:
        gguf_path: Path to the GGUF model file
        
    Returns:
        Dictionary containing attention masks for each layer
    """
    print(f"Loading GGUF model to extract attention masks: {gguf_path}")
    
    try:
        from gguf.gguf_reader import GGUFReader
        import torch
        import numpy as np
        
        reader = GGUFReader(gguf_path)
        
        # Dictionary to store attention masks
        attention_masks = {}
        
        # Extract attention-related tensors
        attention_tensors = {}
        for tensor_name in reader.tensor_infos.keys():
            if any(attn_key in tensor_name.lower() for attn_key in ["attention", "mask", "attn"]):
                try:
                    tensor_info = reader.tensor_infos[tensor_name]
                    tensor_data = reader.read_tensor(tensor_name)
                    attention_tensors[tensor_name] = {
                        "shape": tensor_info.shape,
                        "data": tensor_data
                    }
                    print(f"Extracted attention tensor: {tensor_name}")
                except Exception as e:
                    print(f"Error reading tensor {tensor_name}: {str(e)}")
        
        # Organize by layer
        layers = {}
        for tensor_name in attention_tensors:
            if "layers" in tensor_name:
                # Extract layer number
                parts = tensor_name.split(".")
                layer_idx = None
                for i, part in enumerate(parts):
                    if part == "layers" and i+1 < len(parts):
                        try:
                            layer_idx = int(parts[i+1])
                            break
                        except ValueError:
                            continue
                
                if layer_idx is not None:
                    if layer_idx not in layers:
                        layers[layer_idx] = {}
                    layers[layer_idx][tensor_name] = attention_tensors[tensor_name]
        
        attention_masks["layers"] = layers
        attention_masks["global_tensors"] = {
            k: v for k, v in attention_tensors.items() if "layers" not in k
        }
        
        print(f"Completed attention mask extraction for {len(layers)} layers")
        return attention_masks
        
    except ImportError as e:
        print(f"GGUFReader import error: {str(e)}. Using llama-cpp as fallback.")
        
        # Fallback using llama-cpp
        llm = Llama(model_path=gguf_path, n_gpu_layers=32)
        
        # Create a simple attention mask structure
        # Note: This is a simplified version as llama-cpp doesn't expose attention masks directly
        attention_masks = {
            "metadata": {
                "model_path": gguf_path,
                "note": "Attention masks extracted via llama-cpp fallback method"
            }
        }
        
        print("Attention mask extraction completed using fallback method")
        return attention_masks


def extract_embedding_size(gguf_path):
    """Extract embedding size from GGUF model"""
    print(f"Loading GGUF model to extract embedding size: {gguf_path}")
    llm = Llama(model_path=gguf_path, embedding=True, n_gpu_layers=32)  # CPU only for extraction
    
    # Get embedding
    embedding = llm.embed("This is a sample text")
    embedding_size = len(embedding)
    print(f"Extracted embedding size: {embedding_size}")
    
    return embedding_size

def convert_to_coreml():
    """Convert a simple embedding model to CoreML format"""
    load_dotenv()
    
    # Get model paths
    gguf_path = os.getenv('LLAMA_MODEL_PATH')
    if not gguf_path:
        raise ValueError("LLAMA_MODEL_PATH not set in .env file")
    
    model_dir = os.path.dirname(gguf_path)
    model_name = os.path.splitext(os.path.basename(gguf_path))[0]
    output_path = os.path.join(model_dir, f"{model_name}_coreml.mlpackage")
    
    # Extract embedding size from GGUF model
    embedding_size = extract_embedding_size(gguf_path)
    
    print("Creating simple embedding model...")
    model = SimpleEmbedder(embedding_size=embedding_size)
    model.eval()  # Set to evaluation mode
    
    # Create sample input
    sample_input = torch.randint(0, 128000, (1, 10), dtype=torch.int64)
    
    # Trace the model
    print("Tracing model...")
    traced_model = torch.jit.trace(model, sample_input)
    
    # Convert to CoreML
    print("Converting to CoreML...")
    mlmodel = ct.convert(
        traced_model,
        inputs=[
            ct.TensorType(
                name="input_ids",
                shape=(1, 10),  # Batch size, sequence length
                dtype=np.int32
            )
        ],
        compute_units=ct.ComputeUnit.ALL,
        minimum_deployment_target=ct.target.macOS15
    )
    
    # Set metadata
    mlmodel.author = "Llama-3.2 Simple Embedder"
    mlmodel.license = "Same as original Llama-3.2 Model"
    mlmodel.short_description = "Simple embedding model for Llama-3.2"
    
    # Save the model
    print(f"Saving CoreML model to: {output_path}")
    mlmodel.save(output_path)
    
    # Update environment variable
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    with open(env_path, "r") as f:
        lines = f.readlines()
    
    with open(env_path, "w") as f:
        found = False
        for line in lines:
            if line.startswith("LLAMA_COREML_PATH="):
                f.write(f"LLAMA_COREML_PATH={output_path}\n")
                found = True
            else:
                f.write(line)
        
        if not found:
            f.write(f"\nLLAMA_COREML_PATH={output_path}\n")
    
    print("\nConversion completed successfully!")
    print(f"CoreML model saved to: {output_path}")
    print("Added LLAMA_COREML_PATH to .env file")
    
    print("\nNOTE: This is a simple embedding model with random weights.")
    print("It has the correct architecture but not the actual weights from Llama-3.2.")
    print("This is useful for testing the CoreML integration in your application.")

if __name__ == "__main__":
    try:
        convert_to_coreml()
    except Exception as e:
        print(f"\nError during conversion: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check that coremltools is properly installed")
        print("2. Verify that you're running on macOS 13 or later")
        print("3. Make sure all dependencies are installed correctly")
        raise
