# Freyja Meta-Attention Layer (FMAL) - CoreML Implementation

This repository contains the CoreML implementation of the Freyja Meta-Attention Layer (FMAL), a system for parsing GGUF Llama models layer by layer and extracting embeddings and attention masks.

## Overview

The FMAL system is designed to create a reflective layer on top of LLMs and EVM-compatible transaction systems. This implementation focuses on:

1. Parsing GGUF Llama models layer by layer
2. Extracting and storing attention masks
3. Extracting embeddings for VectorDB storage
4. Converting models to CoreML format for efficient inference on Apple devices

## Key Components

- `get_embeddings_from_gguf_model.py`: Extracts embeddings from GGUF models and converts to CoreML
- `gguf_reader.py`: Utilities for reading and parsing GGUF model files

## Usage

### Environment Setup

Create a `.env` file with the following variables:

```
LLAMA_MODEL_PATH=/path/to/your/llama/model.gguf
```

### Extract Embeddings and Convert to CoreML

```bash
python get_embeddings_from_gguf_model.py
```

This will:
1. Extract embeddings from the GGUF model
2. Create a simple embedding model
3. Convert the model to CoreML format
4. Save the CoreML model and update the `.env` file with its path

### Extract Model Structure

```bash
python gguf_reader.py
```

This will:
1. Extract the chat template from the model
2. Parse the complete model structure
3. Print information about the model layers

## Requirements

- Python 3.9+
- PyTorch
- CoreMLTools
- llama-cpp-python
- python-dotenv
- gguf (for reading GGUF files)

## Architecture

The implementation follows the Freyja Meta-Attention Layer architecture as described in `ARCHITECTURE.MD`.

## Notes

- The CoreML model created is a simple embedding model with the correct architecture but random weights
- For full functionality, the extracted embeddings and attention masks should be stored in a VectorDB and GraphDB respectively
huggingface_hub
