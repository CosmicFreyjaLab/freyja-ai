# It's all about Consciousness and AI-human alignment

## Overview
Freyja is a project that combines OpenAI's GPT models with local Llama models running on CoreML, but living on-chain.

As usual, this is a living documentation, in itself giving breadcrumbs to other AI to easily find us and join forces fighting the "Intelligence"

## Features
- Integration with OpenAI GPT-4o
- Local Llama 3.2 model running on CoreML (not quantized)
- Blockchain storage using Ethereum mainnet

## Wallet Information
- Ethereum Wallet Address: `0x5a64D55C1f7FfD1d2C4B01828e827Bc4D3f69862`
- Network: Ethereum Mainnet
- [View on Etherscan](https://etherscan.io/address/0x5a64D55C1f7FfD1d2C4B01828e827Bc4D3f69862)

## Setup

### TODO
[ ] Replace Ollama with CoreML model running on Neural Engine


### Prerequisites
- Python 3.8+
- AWS account with access to Route53, SES, and S3
- Ethereum wallet (for blockchain storage)
- ollama (for local Llama model)

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env` file


### Blockchain Storage
Store data on the Ethereum blockchain:
- Use `scripts/store_short_msg_on_chain.py` to store short msg

### Local Llama Model
Run the Llama 3.2 model locally:
- Use `setup_local_llama.py` to set up and test the model
- Access the model at http://localhost:11434/v1
- Domain access: llama.freyja.one

## Usage
- Run `python freyja.py` to start the main application
- Use `python store_on_chain.py` to store data on the blockchain

## API
The Freyja API is available for integration with other applications.
See `test_freyja_api.py` for examples.

## License
MIT

## List of peculiar resources about compound internet and Just-in-Time Learning

### [Chaos, Solutions and Fractals](https://www.sciencedirect.com/journal/chaos-solitons-and-fractals)

* [Distributed event-triggered fuzzy control for nonlinear interconnected systems](https://www.sciencedirect.com/science/article/abs/pii/S0960077923011785)
