#!/usr/bin/env python3
"""
================================================================================
           UNREAL ENGINE 5 WIDESCREEN & ULTRAWIDE EXECUTABLE PATCHER
================================================================================
Target Game: Rune Factory: Guardians of Azuma (and other Unreal Engine 5 games)
Supported OS: Windows, Linux (Bottles/Steam/Proton), macOS (Crossover/Whisky)
Version: 1.1.0
Written By: AI Coding Assistant pair programming with Michael

DESCRIPTION:
  This script patches hardcoded 16:9 aspect ratio locks in Unreal Engine 5
  executable binaries (Game-Win64-Shipping.exe).

  It creates a safe backup (.bak) of the original file, reads the original
  binary data, dynamically searches for float32 aspect ratio constants
  (1.7777777 / 16:9), replaces them with the float32 representation of your
  desired aspect ratio (e.g. 21:9, 32:9, or a custom ratio), and saves the
  newly patched executable.

  For UNIX systems (Linux/macOS), it also handles file permission unlocking
  and locks the final patched executable as Read-Only to prevent the engine
  from resetting it upon launch.

  v1.1.0 ALSO fixes a GameUserSettings.ini side-effect where the aspect ratio
  patch causes the engine to render at 135% supersampling (e.g. 4644x1944
  instead of native 3440x1440). The ini fixer searches common Wine/Proton/
  Bottles/CrossOver paths automatically and resets the resolution quality
  setting to native (100%).

HOW TO USE:
  1. Place this script directly in your game folder next to the executable:
     [GameInstallDir]/game/Game/Binaries/Win64/
  2. Run the script!
     - Windows: Double-click or run 'python rune_factory_azuma_ultrawide_patcher.py'
     - Linux/macOS: Open a terminal in the folder and run:
       chmod +x rune_factory_azuma_ultrawide_patcher.py
       ./rune_factory_azuma_ultrawide_patcher.py
  3. Choose your desired option from the menu.
================================================================================
"""

import os
import re
import sys
import glob
import shutil
import struct
import platform

VERSION    = "1.1.0"
TARGET_EXE = "Game-Win64-Shipping.exe"
BACKUP_EXT = ".bak"
GAME_NAME  = "Rune Factory Guardians of Azuma"
INI_REL    = os.path.join("Saved", "Config", "Windows", "GameUserSettings.ini")


# ---------------------------------------------------------------------------
# Executable patching
# ---------------------------------------------------------------------------

def get_hex_from_ratio(ratio):
    """Convert a float aspect ratio to its little-endian IEEE 754 float32 bytes."""
    return struct.pack('<f', ratio)


def patch_exe(exe_path, target_ratio, ratio_name, display_width, display_height):
    """
    Patch the executable and fix the accompanying GameUserSettings.ini.

    1. Creates a .bak backup if one does not exist.
    2. Reads binary data from the backup (always patches from the clean source).
    3. Replaces all 16:9 float32 patterns with the target aspect ratio.
    4. Writes the patched binary and marks it read-only.
    5. Locates and repairs GameUserSettings.ini so the engine renders at native
       resolution instead of triggering unintended supersampling.
    """
    bak_path = exe_path + BACKUP_EXT

    # --- Step 1: backup ---
    if not os.path.exists(bak_path):
        print(f"[*] Creating backup: {bak_path}")
        try:
            shutil.copyfile(exe_path, bak_path)
            print("[+] Backup created.")
        except Exception as e:
            print(f"[-] Backup failed: {e}")
            return
    else:
        print("[*] Backup already exists. Patching from backup...")

    # --- Step 2: read from backup ---
    try:
        with open(bak_path, "rb") as f:
            data = bytearray(f.read())
    except Exception as e:
        print(f"[-] Could not read backup: {e}")
        return

    # 16:9 = 1.77777777... Two slightly different float32 representations
    # appear in UE5 shipping builds (differ by 2 ULPs due to compiler rounding).
    pattern1    = b"\x39\x8E\xE3\x3F"
    pattern2    = b"\x3B\x8E\xE3\x3F"
    replacement = get_hex_from_ratio(target_ratio)

    print(f"[*] Target: {ratio_name}  ({target_ratio:.6f})")
    print(f"[*] Replacement bytes: {replacement.hex().upper()}")

    # --- Step 3: search and replace ---
    count1 = count2 = 0
    idx = 0
    while True:
        idx = data.find(pattern1, idx)
        if idx == -1:
            break
        data[idx:idx+4] = replacement
        count1 += 1
        idx += 4

    idx = 0
    while True:
        idx = data.find(pattern2, idx)
        if idx == -1:
            break
        data[idx:idx+4] = replacement
        count2 += 1
        idx += 4

    total = count1 + count2
    print(f"[+] Replaced {count1} × pattern1  +  {count2} × pattern2  =  {total} total")

    if total == 0:
        print("[-] No 16:9 patterns found. The exe may already be patched or is incompatible.")
        return

    # --- Step 4: write and lock ---
    try:
        if os.path.exists(exe_path):
            os.chmod(exe_path, 0o644)
        with open(exe_path, "wb") as f:
            f.write(data)
        os.chmod(exe_path, 0o444)
        print("[+] Executable patched and locked read-only.")
    except Exception as e:
        print(f"[-] Write failed: {e}")
        return

    # --- Step 5: fix ini ---
    print()
    fix_game_user_settings(display_width, display_height)


# ---------------------------------------------------------------------------
# GameUserSettings.ini repair
# ---------------------------------------------------------------------------

def find_game_user_settings():
    """
    Search common Wine/Proton/Bottles/CrossOver paths for the game's
    GameUserSettings.ini and return a list of all found paths.
    """
    home   = os.path.expanduser("~")
    system = platform.system()
    found  = []

    if system == "Windows":
        local = os.environ.get("LOCALAPPDATA", "")
        found.append(os.path.join(local, GAME_NAME, INI_REL))

    elif system == "Linux":
        # Bottles – Flatpak install
        found += glob.glob(os.path.join(
            home, ".var/app/com.usebottles.bottles/data/bottles/bottles",
            "*", "drive_c", "users", "*", "AppData", "Local", GAME_NAME, INI_REL))
        # Bottles – native install
        found += glob.glob(os.path.join(
            home, ".local/share/bottles/bottles",
            "*", "drive_c", "users", "*", "AppData", "Local", GAME_NAME, INI_REL))
        # Steam / Proton (common paths)
        for steam_root in [
            os.path.join(home, ".steam", "steam"),
            os.path.join(home, ".local", "share", "Steam"),
        ]:
            found += glob.glob(os.path.join(
                steam_root, "steamapps", "compatdata", "*", "pfx",
                "drive_c", "users", "*", "AppData", "Local", GAME_NAME, INI_REL))

    elif system == "Darwin":
        # CrossOver
        found += glob.glob(os.path.join(
            home, "Library", "Application Support", "CrossOver", "Bottles",
            "*", "drive_c", "users", "*", "AppData", "Local", GAME_NAME, INI_REL))
        # Whisky
        found += glob.glob(os.path.join(
            home, "Library", "Containers", "com.isaacmarovitz.Whisky", "Bottles",
            "*", "drive_c", "users", "*", "AppData", "Local", GAME_NAME, INI_REL))

    return [p for p in found if os.path.exists(p)]


def fix_game_user_settings(width, height):
    """
    Repair GameUserSettings.ini after patching the exe.

    Background: patching the exe's aspect ratio constants causes the engine's
    resolution-selection code to pick an unintended supersampled render target
    (e.g. 4644x1944 on a 3440x1440 display — 135% of native). This happens
    because sg.ResolutionQuality gets written as 0 during the first patched
    launch, which maps to a non-native screen percentage in this game's custom
    scalability configuration.

    Fix: set sg.ResolutionQuality=100 (native render scale) and reset
    ResolutionSizeX/Y to match the target display resolution so the game
    starts cleanly at native resolution.
    """
    ini_files = find_game_user_settings()

    if not ini_files:
        print("[!] GameUserSettings.ini not found — skipping ini fix.")
        print("    If the game renders at an inflated resolution (e.g. 4644x1944),")
        print("    manually set  sg.ResolutionQuality=100  in your ini file.")
        return

    for ini_path in ini_files:
        print(f"[*] Fixing ini: {ini_path}")
        try:
            with open(ini_path, "r", encoding="utf-8") as f:
                content = f.read()
            original = content

            content = re.sub(r'sg\.ResolutionQuality=\d+',
                             'sg.ResolutionQuality=100', content)
            content = re.sub(r'(?m)^ResolutionSizeX=\d+',
                             f'ResolutionSizeX={width}', content)
            content = re.sub(r'(?m)^ResolutionSizeY=\d+',
                             f'ResolutionSizeY={height}', content)
            content = re.sub(r'(?m)^LastUserConfirmedResolutionSizeX=\d+',
                             f'LastUserConfirmedResolutionSizeX={width}', content)
            content = re.sub(r'(?m)^LastUserConfirmedResolutionSizeY=\d+',
                             f'LastUserConfirmedResolutionSizeY={height}', content)
            content = re.sub(r'(?m)^DesiredScreenWidth=\d+',
                             f'DesiredScreenWidth={width}', content)
            content = re.sub(r'(?m)^DesiredScreenHeight=\d+',
                             f'DesiredScreenHeight={height}', content)

            if content != original:
                with open(ini_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"[+] Fixed — resolution reset to {width}x{height} @ native quality.")
            else:
                print("[=] Ini already looks correct, no changes needed.")
        except Exception as e:
            print(f"[-] Ini fix error: {e}")


# ---------------------------------------------------------------------------
# Restore
# ---------------------------------------------------------------------------

def restore_backup(exe_path):
    """Restore the original 16:9 executable from the .bak backup."""
    bak_path = exe_path + BACKUP_EXT
    if not os.path.exists(bak_path):
        print(f"[-] No backup found at: {bak_path}")
        return
    print("[*] Restoring original executable...")
    try:
        if os.path.exists(exe_path):
            os.chmod(exe_path, 0o644)
        shutil.copyfile(bak_path, exe_path)
        print("[+] Restored original 16:9 executable.")
        print()
        print("[*] Note: GameUserSettings.ini is not reverted automatically.")
        print("    The game will rewrite it with correct values on next launch.")
    except Exception as e:
        print(f"[-] Restore error: {e}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print("=" * 52)
    print(f"  UE5 Widescreen & Ultrawide Patcher  v{VERSION}")
    print("=" * 52)

    # Locate the target executable
    current_dir = os.path.dirname(os.path.realpath(__file__))
    exe_path    = os.path.join(current_dir, TARGET_EXE)

    if not os.path.exists(exe_path):
        print(f"[-] {TARGET_EXE} not found in script directory.")
        user_input = input(f"[?] Enter path to {TARGET_EXE} (or its folder): ").strip()
        user_input = user_input.replace('"', '').replace("'", "")
        if os.path.isdir(user_input):
            exe_path = os.path.join(user_input, TARGET_EXE)
        else:
            exe_path = user_input

    if not os.path.exists(exe_path) or not exe_path.endswith(TARGET_EXE):
        print(f"[-] Invalid path: {exe_path}")
        input("\nPress Enter to exit...")
        sys.exit(1)

    print(f"[+] Found: {exe_path}\n")

    print("Select an option:")
    print("  1) Patch for 21:9  (3440×1440, 2560×1080)")
    print("  2) Patch for 32:9  (5120×1440, 3840×1080)")
    print("  3) Patch for a custom aspect ratio")
    print("  4) Restore original 16:9 from backup")
    print("  5) Fix GameUserSettings.ini only (no exe patch)")
    print("  6) Exit")

    choice = input("\nEnter choice (1-6): ").strip()

    if choice == "1":
        patch_exe(exe_path, 3440.0 / 1440.0, "21:9 Widescreen", 3440, 1440)

    elif choice == "2":
        patch_exe(exe_path, 5120.0 / 1440.0, "32:9 Super-Ultrawide", 5120, 1440)

    elif choice == "3":
        try:
            w = float(input("[?] Display width  (e.g. 3840): ").strip())
            h = float(input("[?] Display height (e.g. 1600): ").strip())
            patch_exe(exe_path, w / h, f"Custom {w:.0f}x{h:.0f}", int(w), int(h))
        except ValueError:
            print("[-] Invalid input.")

    elif choice == "4":
        restore_backup(exe_path)

    elif choice == "5":
        try:
            w = int(input("[?] Your display width  (e.g. 3440): ").strip())
            h = int(input("[?] Your display height (e.g. 1440): ").strip())
            fix_game_user_settings(w, h)
        except ValueError:
            print("[-] Invalid input.")

    elif choice == "6":
        print("Exiting.")

    else:
        print("[-] Invalid choice.")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
