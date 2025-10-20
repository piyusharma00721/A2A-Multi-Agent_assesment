#!/usr/bin/env python3
"""
Installation script for Multi-Agent Query Router dependencies
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Main installation function"""
    print("🔧 Installing Multi-Agent Query Router Dependencies")
    print("=" * 50)
    
    # Read requirements from file
    try:
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print("❌ requirements.txt not found!")
        return False
    
    print(f"Found {len(requirements)} packages to install...")
    
    # Install each package
    failed_packages = []
    for package in requirements:
        print(f"\n📦 Installing {package}...")
        if not install_package(package):
            failed_packages.append(package)
    
    # Summary
    print("\n" + "=" * 50)
    if failed_packages:
        print(f"⚠️  Installation completed with {len(failed_packages)} failures:")
        for package in failed_packages:
            print(f"  - {package}")
        print("\nYou may need to install these packages manually.")
    else:
        print("✅ All packages installed successfully!")
    
    print("\nNext steps:")
    print("1. Set your GOOGLE_API_KEY environment variable")
    print("2. Run: python main.py --help")
    
    return len(failed_packages) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
