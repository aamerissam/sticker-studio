# Karim Sticker Studio - Windows Installer Guide

> **Version:** 1.0.0 | **Last updated:** August 2026

---

## Quick Fix: If build.bat fails with weird errors

If you see errors like `'Karim' is not recognized` or `'cho' is not recognized`,
your batch file got corrupted by encoding. **Use Method B below.**

---

## Method A: build.bat (fastest when it works)

1. Copy `build.bat` to your project folder (next to `main.py`).
2. Double-click it, or open CMD and run:
   ```cmd
   build.bat
   ```

> **Note:** The batch file must be saved with **Windows (CRLF)** line endings
> and **no BOM**. If you edited it in Notepad++ or VS Code, set:
> - Line endings: `CRLF`
> - Encoding: `UTF-8` (NOT "UTF-8 BOM")

---

## Method B: build.py (recommended - never fails)

1. Copy `build.py` to your project folder.
2. Open CMD or PowerShell in that folder.
3. Run:
   ```cmd
   python build.py
   ```

This does the exact same thing as `build.bat` but avoids all Windows
encoding/line-ending issues.

---

## Method C: Manual commands

If both scripts fail, run these commands one by one in CMD:

```cmd
pip install pyinstaller
pip install -r requirements.txt
pyinstaller --onefile --windowed --name "KarimStickerStudio" --hidden-import PIL._tkinter_finder --hidden-import qrcode.image.pil --clean main.py
```

---

## Build the Windows Installer (Inno Setup)

After `dist\KarimStickerStudio.exe` exists:

1. Install **Inno Setup** from [jrsoftware.org](https://jrsoftware.org/isdl.php)
2. Open `KarimStickerStudio.iss` in Inno Setup Compiler
3. **IMPORTANT:** Replace the placeholder GUID with a real one from [guidgenerator.com](https://www.guidgenerator.com)
4. Press **F9** to compile
5. Your installer will be at: `installer_output\KarimStickerStudio_Setup.exe`

---

## File Structure After Setup

```
karim-sticker-studio/
├── app.py                          (existing)
├── config.py                       (existing)
├── main.py                         (existing - must have def main():)
├── requirements.txt                (existing)
├── build.bat                       (new - Method A)
├── build.py                        (new - Method B - RECOMMENDED)
├── KarimStickerStudio.iss          (new - Inno Setup script)
├── pyproject.toml                  (new - optional pip install)
└── GUIDE.md                        (this file)
```

---

## End-User Install / Uninstall

| Action | How |
|--------|-----|
| **Install** | Double-click `KarimStickerStudio_Setup.exe` |
| **Launch** | Start Menu -> Karim Sticker Studio |
| **Uninstall** | Settings -> Apps -> Karim Sticker Studio -> Uninstall |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `'Karim' is not recognized` | Batch file encoding is wrong. Use **Method B** (`python build.py`) |
| `pyinstaller not found` | Run `pip install pyinstaller` manually first |
| `.exe opens then closes` | Run from CMD to see error: `dist\KarimStickerStudio.exe` |
| `ModuleNotFoundError` | Add `--hidden-import <module>` to the build command |
| Inno Setup won't compile | Make sure you replaced the placeholder GUID |
