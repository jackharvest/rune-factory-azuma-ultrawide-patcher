#!/usr/bin/env python3
"""
================================================================================
           UNREAL ENGINE 5 WIDESCREEN & ULTRAWIDE EXECUTABLE PATCHER
================================================================================
Target Game: Rune Factory: Guardians of Azuma (and other Unreal Engine 5 games)
Supported OS: Windows, Linux (Bottles/Steam/Proton), macOS (Crossover/Whisky)
Written By: AI Coding Assistant pair programming with Michael

DESCRIPTION:
  This script patches hardcoded 16:9 aspect ratio locks in Unreal Engine 5 
  executable binaries (specifically Game-Win64-Shipping.exe). 
  It creates a safe backup (.bak) of the original file, reads the original 
  binary data, dynamically searches for float32 aspect ratio constants 
  (1.7777777 / 16:9), replaces them with the float32 representation of your 
  desired aspect ratio (e.g. 21:9, 32:9, or a custom ratio), and saves the 
  newly patched executable.
  
  For UNIX systems (Linux/macOS), it also handles file permission unlocking
  and locks the final patched executable as Read-Only to prevent the engine 
  from resetting it upon launch.

HOW TO USE:
  1. Place this script directly in your game folder next to the executable:
     [GameInstallDir]/game/Game/Binaries/Win64/
  2. Run the script!
     - Windows: Double-click or run 'python rune_factory_azuma_ultrawide_patcher.py' in Cmd/PowerShell.
     - Linux/macOS: Open a terminal in the folder and run:
       chmod +x rune_factory_azuma_ultrawide_patcher.py
       ./rune_factory_azuma_ultrawide_patcher.py
  3. Choose your desired option from the menu.
================================================================================
"""

import os
import sys
import shutil
import struct

# The target executable name we are searching for and patching
TARGET_EXE = "Game-Win64-Shipping.exe"
# The extension to append to the backup file
BACKUP_EXT = ".bak"

def get_hex_from_ratio(ratio):
    """
    Converts a floating-point aspect ratio (like 2.3888) into its exact 
    little-endian IEEE 754 float32 byte representation.
    """
    return struct.pack('<f', ratio)

def patch_exe(exe_path, target_ratio, ratio_name):
    """
    Handles the binary patching of the executable.
    1. Creates a backup if one doesn't exist.
    2. Reads the original bytes from the backup.
    3. Finds and replaces all 16:9 aspect ratio floats with the new ratio.
    4. Writes the patched bytes back to the main executable path.
    5. Sets file permissions appropriately.
    """
    bak_path = exe_path + BACKUP_EXT
    
    # 1. Create a safe backup of the original unmodified game executable
    if not os.path.exists(bak_path):
        print(f"[*] Creating backup of original executable at: {bak_path}")
        try:
            shutil.copyfile(exe_path, bak_path)
            print("[+] Backup created successfully.")
        except Exception as e:
            print(f"[-] Error creating backup: {e}")
            return
    else:
        print("[*] Original backup already exists. Proceeding with fresh patch...")

    # 2. Always read data from the unmodified backup to prevent corrupting 
    # the executable if running the patcher multiple times.
    print(f"[*] Reading original data from backup: {bak_path}...")
    try:
        with open(bak_path, "rb") as f:
            data = bytearray(f.read())
    except Exception as e:
        print(f"[-] Error reading backup file: {e}")
        return

    # Unreal Engine 5 default aspect ratio pattern definitions.
    # 16:9 is 1.77777777... In IEEE 754 float32, this is represented as 3f e3 8e 39.
    # Because PCs are little-endian, the bytes are stored reversed: 39 8E E3 3F.
    # Some parts of the engine calculate or store it slightly differently: 3B 8E E3 3F.
    pattern1 = b"\x39\x8E\xE3\x3F"
    pattern2 = b"\x3B\x8E\xE3\x3F"
    
    # Calculate the exact hex representation of the replacement ratio
    replacement = get_hex_from_ratio(target_ratio)

    print(f"[*] Target aspect ratio: {ratio_name} ({target_ratio:.4f})")
    print(f"[*] Replacing 16:9 patterns with: {replacement.hex().upper()}")

    # 3. Perform a binary search and replace on the executable bytearray
    count1 = 0
    count2 = 0

    # Search and replace all instances of pattern 1
    idx = 0
    while True:
        idx = data.find(pattern1, idx)
        if idx == -1:
            break
        data[idx:idx+4] = replacement
        count1 += 1
        idx += 4

    # Search and replace all instances of pattern 2
    idx = 0
    while True:
        idx = data.find(pattern2, idx)
        if idx == -1:
            break
        data[idx:idx+4] = replacement
        count2 += 1
        idx += 4

    print(f"[+] Replaced {count1} instances of pattern '398EE33F'")
    print(f"[+] Replaced {count2} instances of pattern '3B8EE33F'")

    # 4. Save the patched data back to the active executable path
    if count1 > 0 or count2 > 0:
        try:
            # If the file exists and was previously marked read-only, we must
            # unlock it (0o644 / owner write) so we can overwrite it.
            if os.path.exists(exe_path):
                os.chmod(exe_path, 0o644)
            
            with open(exe_path, "wb") as f:
                f.write(data)
            
            # Lock the patched file as Read-Only (0o444).
            # This is a critical step because some Unreal Engine games will actively 
            # rewrite or reset their executable file parameters upon launch.
            os.chmod(exe_path, 0o444)
            print("[+] Executable successfully patched and marked as Read-Only!")
        except Exception as e:
            print(f"[-] Error writing patched executable: {e}")
    else:
        print("[-] No matching 16:9 patterns found! The executable might already be patched or is not a compatible UE5 executable.")

def restore_backup(exe_path):
    """
    Reverts the patched executable back to the original unmodified state by 
    copying the .bak file back over the .exe file.
    """
    bak_path = exe_path + BACKUP_EXT
    if not os.path.exists(bak_path):
        print(f"[-] No backup file found at: {bak_path}")
        return
    
    print(f"[*] Restoring original executable from backup...")
    try:
        # Unlock the patched file if it is read-only
        if os.path.exists(exe_path):
            os.chmod(exe_path, 0o644)
        
        # Copy the original backup over the patched executable
        shutil.copyfile(bak_path, exe_path)
        print("[+] Successfully restored original 16:9 executable.")
    except Exception as e:
        print(f"[-] Error restoring backup: {e}")

def main():
    print("====================================================")
    print("   Unreal Engine 5 Widescreen & Ultrawide Patcher   ")
    print("====================================================")
    
    # Attempt to locate the target executable relative to this script's directory.
    # This makes running the script effortless if it is placed in the game folder.
    current_dir = os.path.dirname(os.path.realpath(__file__))
    exe_path = os.path.join(current_dir, TARGET_EXE)
    
    if not os.path.exists(exe_path):
        # If the script is run from outside the game folder (e.g. from the Desktop),
        # gracefully ask the user to specify where the executable is located.
        print(f"[-] Could not find {TARGET_EXE} in the script directory.")
        user_input = input(f"[?] Enter the absolute folder path or full path to {TARGET_EXE}: ").strip()
        
        # Clean terminal quotes (e.g., if the user drags and drops the folder into terminal)
        user_input = user_input.replace('"', '').replace("'", "")
        
        if os.path.isdir(user_input):
            exe_path = os.path.join(user_input, TARGET_EXE)
        else:
            exe_path = user_input

    # Safety check to ensure we are actually targeting the correct file
    if not os.path.exists(exe_path) or not exe_path.endswith(TARGET_EXE):
        print(f"[-] Invalid file path: {exe_path}. The file must be named exactly {TARGET_EXE}")
        input("\nPress Enter to exit...")
        sys.exit(1)

    print(f"[+] Found Target Executable: {exe_path}\n")
    print("Select an option:")
    print("1) Patch for 21:9 Aspect Ratio (e.g., 3440×1440, 2560×1080)")
    print("2) Patch for 32:9 Aspect Ratio (e.g., 5120×1440, 3840×1080)")
    print("3) Patch for a Custom Aspect Ratio (e.g. 3840×1600 / 24:10)")
    print("4) Restore original 16:9 layout from backup")
    print("5) Exit")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        patch_exe(exe_path, 3440.0 / 1440.0, "21:9 Widescreen")
    elif choice == "2":
        patch_exe(exe_path, 3840.0 / 1080.0, "32:9 Super-Ultrawide")
    elif choice == "3":
        try:
            width = float(input("[?] Enter display width (e.g., 3840): ").strip())
            height = float(input("[?] Enter display height (e.g., 1600): ").strip())
            ratio = width / height
            patch_exe(exe_path, ratio, f"Custom {width:.0f}x{height:.0f}")
        except ValueError:
            print("[-] Invalid input. Width and Height must be numbers.")
    elif choice == "4":
        restore_backup(exe_path)
    elif choice == "5":
        print("Exiting patcher.")
    else:
        print("[-] Invalid choice.")
        
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
