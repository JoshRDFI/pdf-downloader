#!/usr/bin/env python3
"""
PDF-Downloader.py - Main launcher for the PDF Downloader application

This script:
1. Creates a virtual environment if it doesn't exist
2. Installs or updates required dependencies
3. Launches the PDF Downloader application
"""

import os
import sys
import subprocess
import platform
import shutil
import site

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BASE_DIR, "venv")

if platform.system() == "Windows":
    PYTHON_EXECUTABLE = os.path.join(VENV_DIR, "Scripts", "python.exe")
    PIP_EXECUTABLE = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    ACTIVATE_SCRIPT = os.path.join(VENV_DIR, "Scripts", "activate")
    SITE_PACKAGES = os.path.join(VENV_DIR, "Lib", "site-packages")
    ICON_PATH = os.path.join(BASE_DIR, "resources", "icon.ico")
    # Create a resources directory if it doesn't exist
    os.makedirs(os.path.join(BASE_DIR, "resources"), exist_ok=True)
    # Create a placeholder icon file if it doesn't exist
    if not os.path.exists(ICON_PATH):
        with open(ICON_PATH, "w") as f:
            f.write("# Placeholder for icon file. Replace with actual .ico file.")
        print(f"Created placeholder icon at {ICON_PATH}. Please replace with an actual .ico file.")
else:  # macOS, Linux, etc.
    PYTHON_EXECUTABLE = os.path.join(VENV_DIR, "bin", "python")
    PIP_EXECUTABLE = os.path.join(VENV_DIR, "bin", "pip")
    ACTIVATE_SCRIPT = os.path.join(VENV_DIR, "bin", "activate")
    SITE_PACKAGES = os.path.join(VENV_DIR, "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")
    ICON_PATH = os.path.join(BASE_DIR, "resources", "icon.png")
    # Create a resources directory if it doesn't exist
    os.makedirs(os.path.join(BASE_DIR, "resources"), exist_ok=True)
    # Create a placeholder icon file if it doesn't exist
    if not os.path.exists(ICON_PATH):
        with open(ICON_PATH, "w") as f:
            f.write("# Placeholder for icon file. Replace with actual .png file.")
        print(f"Created placeholder icon at {ICON_PATH}. Please replace with an actual .png file.")

REQUIREMENTS_FILE = os.path.join(BASE_DIR, "requirements.txt")
MAIN_SCRIPT = os.path.join(BASE_DIR, "src", "main.py")


def create_venv():
    """Create a virtual environment if it doesn't exist."""
    if not os.path.exists(VENV_DIR):
        print("Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
            print("Virtual environment created successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            sys.exit(1)
    return False


def install_requirements():
    """Install or update required dependencies."""
    print("Installing/updating dependencies...")
    try:
        subprocess.run([PIP_EXECUTABLE, "install", "-U", "pip"], check=True)
        subprocess.run([PIP_EXECUTABLE, "install", "-r", REQUIREMENTS_FILE], check=True)
        print("Dependencies installed/updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)


def launch_application():
    """Launch the PDF Downloader application."""
    print("Launching PDF Downloader...")
    try:
        # Use the Python executable from the virtual environment
        subprocess.run([PYTHON_EXECUTABLE, MAIN_SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error launching application: {e}")
        sys.exit(1)


def main():
    """Main function to set up and launch the application."""
    # Create virtual environment if it doesn't exist
    venv_created = create_venv()
    
    # Install or update dependencies
    install_requirements()
    
    # If we just created the venv, we need to restart the script to use the new environment
    if venv_created:
        print("Virtual environment set up. Restarting launcher...")
        # Restart the script to use the new environment
        if platform.system() == "Windows":
            os.execv(PYTHON_EXECUTABLE, [PYTHON_EXECUTABLE, __file__])
        else:
            os.execv(PYTHON_EXECUTABLE, [PYTHON_EXECUTABLE, __file__])
    
    # Launch the application
    launch_application()


if __name__ == "__main__":
    main()