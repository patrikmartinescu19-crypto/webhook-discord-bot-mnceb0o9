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
    assets_dir = os.path.join(app_dir, "assets")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "Undetected",
        f"--icon={os.path.join(assets_dir, 'icon.ico')}",
        f"--add-data={assets_dir}{os.pathsep}assets",
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
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
