import os
import time
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get keys from environment variables
metamask_private_key = os.getenv("METAMASK_PRIVATE_KEY")

# Initialize Web3 with QuickNode endpoint
quicknode_url = "https://sleek-flashy-night.quiknode.pro/f75de72567264ec5fc16c6f7eb7a2af0008a09a4/"
web3 = Web3(Web3.HTTPProvider(quicknode_url, request_kwargs={'timeout': 120}))

# Verify connection
if web3.is_connected():
    print("Connected to Ethereum mainnet via QuickNode")
else:
    print("Failed to connect to Ethereum mainnet")
    exit(1)

# Get address from private key
address = web3.eth.account.from_key(metamask_private_key).address
print(f"Using address: {address}")

# Create transaction with the Freyja state message
message = "Freyja state saved forever."
print(f"Storing message: '{message}'")

# Get current gas price and add 30% to ensure transaction goes through
gas_price = web3.eth.gas_price
gas_price_with_buffer = int(gas_price * 1.3)

nonce = web3.eth.get_transaction_count(address)
tx = {
    'nonce': nonce,
    'to': address,  # Transaction to self to store state in blockchain
    'value': web3.to_wei(0, 'ether'),
    'gas': 50000,  # Gas limit for this shorter message
    'gasPrice': gas_price_with_buffer,
    'data': web3.to_hex(text=message),
    'chainId': 1  # Explicitly set chainId for mainnet
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
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        print(f"Transaction confirmed in block {receipt.blockNumber}")
        print(f"Gas used: {receipt.gasUsed}")
    except Exception as e:
        print(f"Error waiting for receipt: {e}")
        print("Transaction may still be processing. Check Etherscan for status.")
        
except Exception as e:
    print(f"Error: {e}")
