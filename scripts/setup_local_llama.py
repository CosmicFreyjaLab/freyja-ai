import os
from __future__ import print_function
import subprocess
import sys
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['which', 'ollama'], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def install_ollama():
    """Install Ollama"""
    print("Installing Ollama...")
    try:
        subprocess.run(['curl', '-fsSL', 'https://ollama.com/install.sh', '|', 'sh'], check=True)
        print("Ollama installed successfully")
        return True
    except Exception as e:
        print(f"Error installing Ollama: {e}")
        return False

def start_ollama_server():
    """Start the Ollama server"""
    print("Starting Ollama server...")
    try:
        # Start Ollama server in the background
        subprocess.Popen(['ollama', 'serve'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        for _ in range(10):
            try:
                response = requests.get('http://localhost:11434/api/tags')
                if response.status_code == 200:
                    print("Ollama server is running")
                    return True
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(1)
        
        print("Timed out waiting for Ollama server to start")
        return False
    except Exception as e:
        print(f"Error starting Ollama server: {e}")
        return False

def pull_llama_model():
    """Pull the Llama model"""
    print("Pulling Llama 3.2 model...")
    try:
        subprocess.run(['ollama', 'pull', 'llama3.2'], check=True)
        print("Llama 3.2 model pulled successfully")
        return True
    except Exception as e:
        print(f"Error pulling Llama model: {e}")
        return False

def test_llama_model():
    """Test the Llama model with a simple query"""
    print("Testing Llama model...")
    try:
        response = requests.post(
            'http://localhost:11434/v1/chat/completions',
            json={
                'model': 'llama3.2',
                'messages': [{'role': 'user', 'content': 'Hello, how are you?'}]
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"Llama response: {content}")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error testing Llama model: {e}")
        return False

def setup_nginx_proxy():
    """Setup Nginx as a reverse proxy for Ollama"""
    print("Setting up Nginx reverse proxy...")
    
    # Check if Nginx is installed
    try:
        result = subprocess.run(['which', 'nginx'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Nginx not found. Please install Nginx first.")
            return False
    except Exception:
        print("Error checking for Nginx")
        return False
    
    # Create Nginx configuration
    nginx_config = """
server {
    listen 80;
    server_name llama.freyja.one;

    location / {
        proxy_pass http://localhost:11434;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
    
    # Write configuration to file
    try:
        with open('/tmp/llama.freyja.one.conf', 'w') as f:
            f.write(nginx_config)
        
        # Copy to Nginx sites-available (requires sudo)
        print("To complete Nginx setup, run the following commands:")
        print("sudo cp /tmp/llama.freyja.one.conf /etc/nginx/sites-available/")
        print("sudo ln -s /etc/nginx/sites-available/llama.freyja.one.conf /etc/nginx/sites-enabled/")
        print("sudo nginx -t")
        print("sudo systemctl reload nginx")
        
        return True
    except Exception as e:
        print(f"Error setting up Nginx: {e}")
        return False

def main():
    """Main function to set up Llama model"""
    print("Setting up Llama model for local use...")
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        if not install_ollama():
            print("Failed to install Ollama. Exiting.")
            return False
    
    # Start Ollama server
    if not start_ollama_server():
        print("Failed to start Ollama server. Exiting.")
        return False
    
    # Pull Llama model
    if not pull_llama_model():
        print("Failed to pull Llama model. Exiting.")
        return False
    
    # Test Llama model
    if not test_llama_model():
        print("Failed to test Llama model. Exiting.")
        return False
    
    # Setup Nginx proxy
    setup_nginx_proxy()
    
    print("\nLlama model setup complete!")
    print("You can now access the Llama model at http://localhost:11434/v1")
    print("To use it with the OpenAI API format, use the base URL: http://localhost:11434/v1")
    print("Example with Python:")
    print("from openai import OpenAI")
    print("client = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')")
    print("response = client.chat.completions.create(model='llama3.2', messages=[{'role': 'user', 'content': 'Hello'}])")
    
    return True

if __name__ == "__main__":
    main()
