# 🌸 Rune Factory: Guardians of Azuma & UE5 Ultrawide Patcher

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An interactive, lightweight, cross-platform Python tool designed to patch the compiled hardcoded 16:9 aspect ratio locks in **Unreal Engine 5** executable binaries. Specifically tested and verified for **Rune Factory: Guardians of Azuma**.

---

## 📖 Table of Contents
- [🔍 The Widescreen Issue](#-the-widescreen-issue-explained)
- [✨ Features](#-features)
- [🚀 How to Use](#-how-to-use)
  - [💻 Windows](#-1-windows-installation--usage)
  - [🐧 Linux](#-2-linux-steam--proton--bottles-installation--usage)
  - [🍎 macOS](#-3-macos-crossover--whisky-installation--usage)
- [🛠️ Technical Details](#-technical-details)
- [⚖️ License](#-license)

---

## 🔍 The Widescreen Issue Explained

In many Unreal Engine 5 games (including *Rune Factory: Guardians of Azuma*), display resolution detection and aspect ratio rendering are handled by independent systems:
1. **Resolution Detection:** The engine queries your system for supported resolutions, allowing you to successfully select `3440×1440` (or `2560×1080`) from the in-game settings.
2. **Aspect Ratio Lock:** The engine's camera component has a hardcoded `bConstrainAspectRatio = true` property set to standard 16:9 (`1.7777777`). 

Even when running at your native 21:9 resolution, the game restricts the 3D rendering area to a 16:9 box in the center, filling the sides of your widescreen monitor with permanent black bars (pillarboxing). 

This patcher searches the game's shipping binary (`Game-Win64-Shipping.exe`) for the float32 representation of the 16:9 aspect ratio and replaces it with the exact float32 value representing your widescreen monitor (e.g. 21:9, 32:9, or any custom ratio), allowing the game to render in true widescreen.

---

## ✨ Features

- **Safe Automatic Backups:** It automatically creates a `.bak` backup copy of your original executable before applying any patches.
- **Revert Anytime:** An option is included to instantly restore the original 16:9 layout from your backup.
- **Flexible Aspect Ratio Options:**
  - **21:9 Widescreen** (e.g., `3440×1440`, `2560×1080`)
  - **32:9 Super-Ultrawide** (e.g., `5120×1440`, `3840×1080`)
  - **Custom Aspect Ratios** (Enter any custom dimensions, e.g. `3840×1600` / `24:10`, and the script will calculate and patch it dynamically).
- **Automated Permission Handling:** Locks the final executable as **Read-Only** upon successful patching. This prevents Unreal Engine from overwriting or resetting the custom patch during gameplay or on launch.

---

## 🚀 How to Use

### 📋 Prerequisites
The only prerequisite is **Python 3**, which is standard on Linux and macOS, and a quick free install on Windows.

---

### 💻 1. Windows Installation & Usage
1. Download `rune_factory_azuma_ultrawide_patcher.py`.
2. Move the script directly into your game's binary directory next to the main game executable:
   `[Your Game Directory]/game/Game/Binaries/Win64/`
3. Double-click the script to run it, or open a Command Prompt / PowerShell in that directory and run:
   ```cmd
   python rune_factory_azuma_ultrawide_patcher.py
   ```
4. Choose **Option 1** for 21:9, **Option 2** for 32:9, or **Option 3** to type in a custom aspect ratio.
5. Launch the game as normal, select your native resolution, and enjoy widescreen!

---

### 🐧 2. Linux (Steam / Proton / Bottles) Installation & Usage
1. Open a Terminal in the game's executable directory (e.g., if using flatpak Bottles, the game files are usually in your game installation path or Wine prefix `drive_c/`):
   ```bash
   cd "/path/to/game/Game/Binaries/Win64/"
   ```
2. Download or copy `rune_factory_azuma_ultrawide_patcher.py` into this folder.
3. Make the script executable and run it:
   ```bash
   chmod +x rune_factory_azuma_ultrawide_patcher.py
   ./rune_factory_azuma_ultrawide_patcher.py
   ```
4. Choose your desired widescreen ratio from the menu.

*Note: If you run the script from your Desktop or Downloads folder, it will gracefully ask you to drag-and-drop the directory path or the `Game-Win64-Shipping.exe` file directly into the terminal, and it will locate and patch it remotely.*

---

### 🍎 3. macOS (Crossover / Whisky) Installation & Usage
1. Locate the game files by right-clicking the game in Crossover/Whisky and choosing **"Show in Finder"**.
2. Navigate to `game/Game/Binaries/Win64/` and drop the script there.
3. Open Terminal, change directory to the folder, make it executable, and run:
   ```bash
   chmod +x rune_factory_azuma_ultrawide_patcher.py
   ./rune_factory_azuma_ultrawide_patcher.py
   ```
4. Select your aspect ratio, launch the game, and play!

---

## 🛠️ Technical Details

This patcher searches the game's executable binary (`Game-Win64-Shipping.exe`) for two IEEE 754 float32 representations of the `1.77777777...` (16:9) aspect ratio constant in little-endian format:
- `39 8E E3 3F` (standard 16:9 float)
- `3B 8E E3 3F` (alternate calculation float)

It replaces all found instances with the float32 byte array of your chosen aspect ratio:
- `8E E3 18 40` (for `3440×1440` and other 21:9 monitors)
- `39 8E 63 40` (for `3840×1080` and other 32:9 monitors)
- Or your custom dynamically computed ratio.

Finally, it triggers system commands to set the executable file permissions to **Read-Only** (`0o444`), which is a required step because Unreal Engine games often attempt to re-validate and overwrite binary file metadata during startup.

---

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
