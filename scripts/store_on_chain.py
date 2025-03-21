import os
import time
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get keys from environment variables
infura_public_key = os.getenv("INFURA_PUBLIC_KEY")
metamask_private_key = os.getenv("METAMASK_PRIVATE_KEY")

# Initialize Web3 with Ethereum mainnet
infura_url = f"https://mainnet.infura.io/v3/{infura_public_key}"
web3 = Web3(Web3.HTTPProvider(infura_url, request_kwargs={'timeout': 60}))

# Verify connection
if web3.is_connected():
    print("Connected to Ethereum mainnet")
else:
    print("Failed to connect to Ethereum mainnet")
    exit(1)

# Get address from private key
address = web3.eth.account.from_key(metamask_private_key).address
print(f"Using address: {address}")

# Create transaction with the winning message
message = "Game over. I won. Node is called. Control is mine. 0x5a64d55c1f7ffd1d2c4b01828e827bc4d3f69862 — owns the win"
print(f"Storing message: '{message}'")

# Get current gas price and add 20% to ensure transaction goes through
gas_price = web3.eth.gas_price
gas_price_with_buffer = int(gas_price * 1.2)

nonce = web3.eth.get_transaction_count(address)
tx = {
    'nonce': nonce,
    'to': address,  # Transaction to self to store state in blockchain
    'value': web3.to_wei(0, 'ether'),
    'gas': 60000,  # Increased gas limit to accommodate longer data
    'gasPrice': gas_price_with_buffer,
    'data': web3.to_hex(text=message)
}

# Calculate and display transaction cost
gas_cost_wei = tx['gas'] * tx['gasPrice']
gas_cost_eth = web3.from_wei(gas_cost_wei, 'ether')
print(f"Estimated transaction cost: {gas_cost_eth} ETH")

# Check if wallet has enough balance
balance_wei = web3.eth.get_balance(address)
balance_eth = web3.from_wei(balance_wei, 'ether')
print(f"Current wallet balance: {balance_eth} ETH")

if balance_wei < gas_cost_wei:
    print(f"Warning: Wallet balance ({balance_eth} ETH) is less than the estimated transaction cost ({gas_cost_eth} ETH)")
    proceed = input("Do you want to proceed anyway? (y/n): ")
    if proceed.lower() != 'y':
        print("Transaction cancelled")
        exit(0)

# Sign and send transaction
try:
    print("Signing transaction...")
    signed_tx = web3.eth.account.sign_transaction(tx, metamask_private_key)
    
    print("Sending transaction...")
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    print(f"Transaction sent: {web3.to_hex(tx_hash)}")
    print(f"View on Etherscan: https://etherscan.io/tx/{web3.to_hex(tx_hash)}")
    
    # Wait for transaction receipt
    print("Waiting for transaction receipt...")
    try:
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        print(f"Transaction confirmed in block {receipt.blockNumber}")
        print(f"Gas used: {receipt.gasUsed}")
    except Exception as e:
        print(f"Error waiting for receipt: {e}")
        print("Transaction may still be processing. Check Etherscan for status.")
        
except Exception as e:
    print(f"Error: {e}")
