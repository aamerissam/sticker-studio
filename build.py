#!/usr/bin/env python3
"""Build script for Karim Sticker Studio - Windows .exe"""
import subprocess
import sys
import os


def run(cmd, desc):
    print(f"\n{'='*50}")
    print(f"  {desc}")
    print(f"{'='*50}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"\nERROR: {desc} failed!")
        input("Press Enter to exit...")
        sys.exit(1)
    return result


def main():
    print("Karim Sticker Studio - Windows Builder")
    print("=" * 50)

    # 1. Install pyinstaller
    run("pip install pyinstaller", "Installing PyInstaller")

    # 2. Install requirements
    run("pip install -r requirements.txt", "Installing app dependencies")

    # 3. Check for custom icon
    icon_flag = ""
    if os.path.exists("assets/icon.ico"):
        icon_flag = ' --icon="assets/icon.ico"'
        print("\n  Icon found: assets/icon.ico")
    else:
        print("\n  No icon found - using default Windows icon")
        print("  (Create assets/icon.ico to use a custom app icon)")

    # 4. Build exe
    run(
        'python -m PyInstaller '
        '--onefile '
        '--windowed '
        '--name "KarimStickerStudio" '
        '--hidden-import PIL._tkinter_finder '
        '--hidden-import qrcode.image.pil '
        '--clean '
        f'{icon_flag} '
        'main.py',
        "Building standalone .exe"
    )

    exe_path = os.path.join("dist", "KarimStickerStudio.exe")
    if os.path.exists(exe_path):
        print("\n" + "=" * 50)
        print("  SUCCESS")
        print(f"  File: {exe_path}")
        print("=" * 50)
    else:
        print("\nWARNING: Build completed but .exe not found at expected path.")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
