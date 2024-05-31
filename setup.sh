#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Update and install dependencies
#sudo apt update
#sudo apt install -y libffi-dev build-essential libssl-dev zlib1g-dev \
#    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
#    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git

# Install pyenv
if [[ ! -d "$HOME/.pyenv" ]]; then
    curl https://pyenv.run | bash
fi

# Add pyenv to path (if this is not added to your bashrc or zshrc)
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"

# Install Python 3.10.2 and set it as global
pyenv install 3.10.2
pyenv global 3.10.2

# Change directory to /work/Interface
cd /work/Interface

# Install npm packages
npm install

# Install Python packages
pip install torch transformers accelerate

# Run the Node.js server
node server.js
