# 🌸 Rune Factory: Guardians of Azuma — UE5 Ultrawide Patcher

![Version](https://img.shields.io/badge/version-1.1.0-brightgreen.svg)
![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A lightweight, cross-platform Python tool that patches the hardcoded 16:9 aspect ratio lock in **Rune Factory: Guardians of Azuma** (and compatible Unreal Engine 5 games) and fixes a related ini bug that causes unintended supersampling on ultrawide monitors.

---

## 📖 Table of Contents
- [🔍 The Widescreen Issue](#-the-widescreen-issue-explained)
- [✨ Features](#-features)
- [🚀 How to Use](#-how-to-use)
  - [💻 Windows](#-1-windows)
  - [🐧 Linux](#-2-linux-steam--proton--bottles)
  - [🍎 macOS](#-3-macos-crossover--whisky)
- [🛠️ Technical Details](#-technical-details)
- [⚠️ Known Limitations](#-known-limitations)
- [📋 Changelog](#-changelog)
- [⚖️ License](#-license)

---

## 🔍 The Widescreen Issue Explained

In *Rune Factory: Guardians of Azuma* (and many other UE5 games), resolution detection and aspect ratio rendering are two separate systems:

1. **Resolution Detection** works fine — you can select `3440×1440` (or any ultrawide resolution) in the in-game settings menu.
2. **Aspect Ratio Lock** is hardcoded — the engine's camera system has `bConstrainAspectRatio = true` set to `1.7777777` (16:9). Even at a 21:9 resolution, the 3D viewport is forced into a 16:9 box with permanent pillarboxing (black bars on the sides).

This patcher finds and replaces the 16:9 float32 constant in the shipping binary with your chosen widescreen ratio.

### The Supersampling Side-Effect (fixed in v1.1)

After patching the exe, the game's resolution-selection code picks up the new aspect ratio constant and — on first launch — incorrectly selects a supersampled render target. For example, on a 3440×1440 monitor it would render at **4644×1944** (135% of native) and write that to `GameUserSettings.ini`. The game would still look correct on screen, but GPU usage was significantly higher than necessary.

v1.1 automatically finds and fixes this ini file after patching the executable, resetting the render resolution to native.

---

## ✨ Features

- **Safe automatic backups** — Creates a `.bak` of the original executable before patching. Always patches from the clean backup so re-running is always safe.
- **Revert anytime** — Option to restore the original 16:9 executable instantly.
- **Flexible aspect ratios:**
  - **21:9** preset (3440×1440, 2560×1080)
  - **32:9** preset (5120×1440, 3840×1080)
  - **Custom** — enter any width × height
- **Read-only lock** — Marks the patched executable read-only to prevent UE5 from overwriting it on launch.
- **GameUserSettings.ini auto-repair** — Automatically finds and fixes the supersampling side-effect across all common Wine/Proton/Bottles/CrossOver install paths. Also available as a standalone option (Option 5) if you only need the ini fix.

---

## 🚀 How to Use

### 📋 Prerequisites

Only **Python 3.7+** is required. It comes pre-installed on Linux and macOS. On Windows, download it from [python.org](https://python.org).

---

### 💻 1. Windows

1. Download `rune_factory_azuma_ultrawide_patcher.py`.
2. Move the script into the game's binary directory next to the executable:
   ```
   [GameDir]\game\Game\Binaries\Win64\
   ```
3. Double-click the script, or open PowerShell in that folder and run:
   ```powershell
   python rune_factory_azuma_ultrawide_patcher.py
   ```
4. Choose **Option 1** for 21:9, **Option 2** for 32:9, or **Option 3** for a custom ratio.
5. Launch the game, set your native resolution in Graphics Settings, and enjoy.

---

### 🐧 2. Linux (Steam / Proton / Bottles)

1. Copy the script into the game's binary folder:
   ```bash
   cd "/path/to/game/Game/Binaries/Win64/"
   ```
2. Make it executable and run it:
   ```bash
   chmod +x rune_factory_azuma_ultrawide_patcher.py
   ./rune_factory_azuma_ultrawide_patcher.py
   ```
3. Choose your ratio from the menu. The script automatically searches Bottles (Flatpak and native), Steam/Proton, and other common paths for `GameUserSettings.ini` and fixes it.

*If the script is not in the game folder, it will prompt you to drag-and-drop the `Game-Win64-Shipping.exe` path into the terminal.*

---

### 🍎 3. macOS (CrossOver / Whisky)

1. Right-click the game in CrossOver or Whisky and choose **Show in Finder**.
2. Navigate to `game/Game/Binaries/Win64/` and place the script there.
3. Open Terminal, `cd` to that folder, and run:
   ```bash
   chmod +x rune_factory_azuma_ultrawide_patcher.py
   ./rune_factory_azuma_ultrawide_patcher.py
   ```
4. Select your aspect ratio. The script searches CrossOver and Whisky bottle paths for the ini file automatically.

---

## 🛠️ Technical Details

### Executable Patching

The patcher searches `Game-Win64-Shipping.exe` for two IEEE 754 float32 representations of `1.77777...` (16:9) in little-endian byte order. Both patterns appear in this UE5 build due to slight compiler rounding differences:

| Pattern | Hex (LE) | Float value |
|---------|----------|-------------|
| Pattern 1 | `39 8E E3 3F` | 1.77777779 |
| Pattern 2 | `3B 8E E3 3F` | 1.77777803 |

All instances are replaced with the target ratio. For reference, the 21:9 replacement for a 3440×1440 display:

| Target | Hex (LE) | Float value |
|--------|----------|-------------|
| 3440×1440 (21:9) | `8E E3 18 40` | 2.38888... |
| 5120×1440 (32:9) | `39 8E 63 40` | 3.55555... |

In the v1.1 analysis, **12 total occurrences** of the 16:9 constant were identified across the binary, falling into four functional groups:

1. **Camera/viewport initializers** (occurrences 1–6): Direct struct field writes that set the aspect ratio and FOV when camera objects are constructed. These are the primary fix for the in-game 3D viewport.
2. **Runtime aspect ratio override** (occurrence 7): A virtual method override on a viewport management class. Controls runtime aspect ratio switching (e.g., the animated 16:9 transitions when entering certain UI screens like shops).
3. **Resolution selection** (occurrences 8–11): Code that builds the list of valid render resolutions constrained to the target aspect ratio. These are responsible for the supersampling side-effect described above.
4. **Static data table** (occurrence 12, `.rdata` section): A pre-existing constant in a float lookup table.

### GameUserSettings.ini Fix

After patching, the engine's resolution selector (occurrences 8–11) can pick a supersampled render target on the first launch. This manifests as `sg.ResolutionQuality=0` and inflated `ResolutionSizeX/Y` values in `GameUserSettings.ini` (for example, 4644×1944 instead of 3440×1440 on a 21:9 display).

The patcher automatically finds the ini file and resets:
- `sg.ResolutionQuality` → `100` (native render scale)
- `ResolutionSizeX/Y` → your actual display resolution
- `LastUserConfirmedResolutionSizeX/Y` → your actual display resolution
- `DesiredScreenWidth/Height` → your actual display resolution

The script searches all common Wine/Proton/Bottles/CrossOver install paths automatically, so no manual path entry is needed.

---

## ⚠️ Known Limitations

- **World Map skew:** The in-game world map may appear skewed or have incorrect icon placement at ultrawide resolutions. This is a separate issue from the main viewport patch. Several in-game UI screens (such as the blacksmith and other shops) correctly transition to a centered 16:9 view when opened — the map does not use this same transition. A fix for the map is under investigation.

- **Save compatibility:** No known issues. Save data is unrelated to the executable patch.

- **Game updates:** If the game updates and overwrites the executable, re-run the patcher. The `.bak` backup will still be present from the previous run and will be re-used as the clean source.

---

## 📋 Changelog

### v1.1.0
- **New:** Automatically locates and repairs `GameUserSettings.ini` after patching, fixing an unintended 135% supersampling render resolution.
- **New:** Standalone ini-only fix option (Option 5) for users who only need the resolution reset.
- **New:** 32:9 preset updated to 5120×1440 dimensions for correct ini resolution.
- **Improved:** Cross-platform ini search covers Bottles (Flatpak + native), Steam/Proton, CrossOver, and Whisky.
- **Improved:** Patcher now reports the total occurrence count on patch (should be 12 for this game version).
- **Docs:** Technical details updated with full analysis of the 12 occurrence groups.

### v1.0.0
- Initial release: exe binary patch for 21:9, 32:9, and custom aspect ratios.

---

## ⚖️ License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
