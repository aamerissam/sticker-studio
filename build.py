#!/usr/bin/env python3
"""Build script for Karim Sticker Studio - Windows .exe"""
import subprocess
import sys
import os
import glob


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

    # Clean up old .spec files to prevent corruption reuse
    for spec in glob.glob("*.spec"):
        print(f"Removing old spec: {spec}")
        os.remove(spec)

    # 1. Install pyinstaller
    run("pip install pyinstaller", "Installing PyInstaller")

    # 2. Install requirements
    run("pip install -r requirements.txt", "Installing app dependencies")

    # 3. Build exe with all hidden imports
    hidden_imports = [
        "app", "config", "qr_generator", "pdf_renderer", "preview_renderer",
        "ui_components", "file_controller", "gallery_controller", "lot_controller",
        "pdf_controller", "preview_controller", "state_controller", "ui_builder",
        "PIL._tkinter_finder", "qrcode.image.pil"
    ]
    hidden_flags = " ".join([f'--hidden-import {m}' for m in hidden_imports])

    run(
        f'python -m PyInstaller '
        f'--onefile '
        f'--windowed '
        f'--name "KarimStickerStudio" '
        f'{hidden_flags} '
        f'--clean '
        f'--noconfirm '
        f'main.py',
        "Building standalone .exe"
    )

    exe_path = os.path.join("dist", "KarimStickerStudio.exe")
    if os.path.exists(exe_path):
        print("\n" + "=" * 50)
        print("  SUCCESS")
        print(f"  File: {exe_path}")
        print("=" * 50)
    else:
        print("\nWARNING: Build completed but .exe not found.")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()