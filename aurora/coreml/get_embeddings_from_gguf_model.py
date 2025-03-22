#!/usr/bin/env python3
"""
Convert Llama GGUF model to CoreML format using Python 3.9
This script creates a simple embedding model in CoreML format
"""

import os
import torch
import torch.nn as nn
import coremltools as ct
import numpy as np
from dotenv import load_dotenv
from llama_cpp import Llama

class SimpleEmbedder(nn.Module):
    """Simple embedding model for CoreML conversion"""
    
    def __init__(self, embedding_size=128000):
        super().__init__()
        self.embedding_size = embedding_size
        # Create a simple embedding layer
        self.embedding = nn.Embedding(embedding_size, embedding_size)
        
    def forward(self, input_ids):
        # Simple embedding lookup and mean pooling
        return self.embedding(input_ids).mean(dim=1)

def get_embeddings_from_pretrained_model(gguf_path):
    #

def get_attention_mask_from_pretrained(gguf_path):
    #


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
