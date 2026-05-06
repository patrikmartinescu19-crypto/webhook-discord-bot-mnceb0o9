"""
Build script for Undetected PC Tweaks.
Creates a standalone .exe using PyInstaller.

Usage:
    pip install pyinstaller
    python build.py
"""
import os
import subprocess
import sys


def build():
    """Build the application into a standalone executable."""
    app_dir = os.path.dirname(os.path.abspath(__file__))

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "Undetected",
        "--hidden-import=customtkinter",
        "--hidden-import=requests",
        "--collect-data=customtkinter",
        os.path.join(app_dir, "app.py"),
    ]

    print("Building Undetected PC Tweaks...")
    print(f"Command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("\nBuild complete! Executable is in the 'dist/' folder.")


if __name__ == "__main__":
    build()
