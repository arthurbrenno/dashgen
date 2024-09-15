#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to print section headers
print_section() {
    echo "==== $1 ===="
}

# Install UV package installer
print_section "Installing UV"
pip install --root-user-action=ignore --upgrade uv

# Update system and install dependencies
print_section "Updating System and Installing Dependencies"
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y \
    build-essential


print_section "Installation Complete"
echo "🧠 Dashgen instalado com êxito! 🎉"
