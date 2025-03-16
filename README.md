# sports_extraction


## Instructions

### 1. Install Firefox

First, update your system and install Firefox.

```bash
sudo apt upgrade
sudo apt update
sudo apt install firefox
```

### 2. Install GeckoDriver
```bash
Download the latest version of GeckoDriver and make it executable.
```
# Download the latest version of GeckoDriver
check availables versions:
https://github.com/mozilla/geckodriver/releases
```bash
wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux-aarch64.tar.gz
```
# Extract the tar file
```bash
tar -xzf geckodriver-v0.34.0-linux-aarch64.tar.gz
```
# Move the geckodriver to /usr/local/bin

```bash
sudo mv geckodriver /usr/local/bin/
```
# Make it executable
```bash
sudo chmod +x /usr/local/bin/geckodriver
```
### 3. Set Up a Python Virtual Environment

# Install virtualenv if not already installed
sudo apt install -y python3-virtualenv

# Create a virtual environment
python3 -m venv sport_env

# Activate the virtual environment
source env/sports_env

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```
### 5. Activate tmux session
check currents sessions 
tmux ls
activate session 
tmux attach name_session

### 6. Execute extraction
```bash
python main1.py
```

### 7. Execute live section 
```bash
python main2.py
```
