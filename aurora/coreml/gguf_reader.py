from gguf.gguf_reader import GGUFReader
import torch.nn as nn
import json


def get_chat_template_str(file_path):
    """
    Extract chat template string from a GGUF model
    
    Args:
        file_path: Path to the GGUF model file
        
    Returns:
        Chat template string if available, None otherwise
    """
    try:
        reader = GGUFReader(file_path)
        
        # Look for chat template in model metadata
        chat_template = None
        
        # Check for tokenizer.chat_template field
        if "tokenizer.chat_template" in reader.fields:
            chat_template = reader.fields["tokenizer.chat_template"].parts
            return chat_template
            
        # Check for other possible field names
        template_field_names = [
            "tokenizer.ggml.chat_template",
            "chat_template",
            "llama.chat_template"
        ]
        
        for field_name in template_field_names:
            if field_name in reader.fields:
                chat_template = reader.fields[field_name].parts
                return chat_template
                
        print(f"No chat template found in {file_path}")
        return None
        
    except Exception as e:
        print(f"Error extracting chat template: {str(e)}")
        return None


def parse_gguf_model_from_pretrained(gguf_model_file):
    """
    Parse a GGUF model and extract embeddings and model structure
    
    Args:
        gguf_model_file: Path to the GGUF model file
        
    Returns:
        Dictionary containing model structure and embeddings
    """
    try:
        # Read model structure using GGUFReader
        reader = GGUFReader(gguf_model_file)
        
        # Extract model metadata
        metadata = {}
        for key, value in reader.fields.items():
            metadata[key] = value.parts
            
        # Extract tensor information
        tensor_info = {}
        for tensor_name, info in reader.tensor_infos.items():
            tensor_info[tensor_name] = {
                "shape": info.shape,
                "type": str(info.tensor_type)
            }
            
        # Create embedding layer from model weights if available
        embedding_tensor_names = [name for name in tensor_info if "embedding" in name.lower()]
        
        if embedding_tensor_names:
            embedding_tensor_name = embedding_tensor_names[0]
            embedding_tensor = reader.read_tensor(embedding_tensor_name)
            
            # Create PyTorch embedding from tensor
            embedding_layer = nn.Embedding.from_pretrained(
                torch.tensor(embedding_tensor),
                freeze=True  # Don't update weights
            )
            
            print(f"Created embedding layer from {embedding_tensor_name}")
            
            return {
                "metadata": metadata,
                "tensor_info": tensor_info,
                "embedding_layer": embedding_layer
            }
        else:
            print("No embedding tensor found in model")
            return {
                "metadata": metadata,
                "tensor_info": tensor_info
            }
            
    except Exception as e:
        print(f"Error parsing GGUF model: {str(e)}")
        return None


def extract_model_structure(gguf_model_file):
    """
    Extract the complete model structure from a GGUF file
    
    Args:
        gguf_model_file: Path to the GGUF model file
        
    Returns:
        Dictionary containing model structure information
    """
    reader = GGUFReader(gguf_model_file)
    
    # Extract model architecture
    architecture = {}
    
    # Get general model info
    general_info = {}
    for key in ["general.name", "general.architecture", "general.file_type"]:
        if key in reader.fields:
            general_info[key] = reader.fields[key].parts
    
    # Get hyperparameters
    hyperparams = {}
    for key in reader.fields:
        if any(param in key for param in ["dim", "hidden_dim", "n_heads", "n_layers", "vocab_size"]):
            hyperparams[key] = reader.fields[key].parts
    
    # Get tensor shapes
    tensor_shapes = {name: info.shape for name, info in reader.tensor_infos.items()}
    
    # Organize by layer
    layers = {}
    for tensor_name in tensor_shapes:
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
                layers[layer_idx][tensor_name] = tensor_shapes[tensor_name]
    
    architecture["general_info"] = general_info
    architecture["hyperparameters"] = hyperparams
    architecture["layers"] = layers
    
    return architecture


if __name__=="__main__":
    model_path = "../models/Llama-3.2-3B-Instruct-f16.gguf"
    
    # Get chat template
    template = get_chat_template_str(model_path)
    if template:
        print(f"Chat template: {template}")
    
    # Extract model structure
    structure = extract_model_structure(model_path)
    print(f"Model structure extracted with {len(structure['layers'])} layers")