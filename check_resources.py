import os
from utils.resource_path import resource_path

# -------------------------------
# Resource Checker for Doom-style Game
# -------------------------------

def check_file(path):
    """Return True if file exists, False otherwise."""
    return os.path.exists(path)

def check_dir(path):
    """Return True if directory exists, False otherwise."""
    return os.path.isdir(path)

def header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

# Expected paths
textures = [
    *[resource_path('resources', 'textures', f'{i}.png') for i in range(1, 6)],
    resource_path('resources', 'textures', 'sky.png'),
    resource_path('resources', 'textures', 'blood_screen.png'),
    resource_path('resources', 'textures', 'gameover.jpg'),
    resource_path('resources', 'textures', 'win.png'),
]
digits = [resource_path('resources', 'textures', 'digits', f'{i}.png') for i in range(0, 11)]

sounds = [
    resource_path('resources', 'sounds', 'shotgun.wav'),
    resource_path('resources', 'sounds', 'npc_pain.wav'),
    resource_path('resources', 'sounds', 'npc_death.wav'),
    resource_path('resources', 'sounds', 'npc_attack.wav'),
    resource_path('resources', 'sounds', 'player_pain.wav'),
    resource_path('resources', 'sounds', 'doom_theme.wav'),
]

sprite_dirs = [
    resource_path('resources', 'sprites', 'npc'),
    resource_path('resources', 'sprites', 'animated_sprites'),
    resource_path('resources', 'sprites', 'static_sprites'),
    resource_path('resources', 'sprites', 'weapons'),
]

# Run checks
header("Checking Main Folders")
main_folders = [resource_path('resources'), resource_path('resources', 'textures'),
                resource_path('resources', 'sounds'), resource_path('resources', 'sprites')]
for folder in main_folders:
    print(f"{folder} -> {'✅ Exists' if check_dir(folder) else '❌ Missing'}")

header("Checking Texture Files")
missing_textures = [p for p in textures if not check_file(p)]
for t in textures:
    print(f"{t} -> {'✅ Found' if check_file(t) else '❌ Missing'}")

header("Checking Digits (0-10).png")
missing_digits = [p for p in digits if not check_file(p)]
for d in digits:
    print(f"{d} -> {'✅ Found' if check_file(d) else '❌ Missing'}")

header("Checking Sound Files")
missing_sounds = [p for p in sounds if not check_file(p)]
for s in sounds:
    print(f"{s} -> {'✅ Found' if check_file(s) else '❌ Missing'}")

header("Checking Sprite Directories")
for d in sprite_dirs:
    print(f"{d} -> {'✅ Exists' if check_dir(d) else '❌ Missing'}")
    if check_dir(d):
        files = os.listdir(d)
        print(f"   contains {len(files)} items: {files[:10]}{'...' if len(files)>10 else ''}")

# Summary
header("SUMMARY")
if not any([missing_textures, missing_digits, missing_sounds]):
    print("🎉 All required files found! You’re good to run the game.")
else:
    print("⚠️ Missing items:")
    if missing_textures:
        print(f"  • Textures missing ({len(missing_textures)}):")
        for t in missing_textures:
            print("    ", t)
    if missing_digits:
        print(f"  • Digit images missing ({len(missing_digits)}):")
        for d in missing_digits:
            print("    ", d)
    if missing_sounds:
        print(f"  • Sounds missing ({len(missing_sounds)}):")
        for s in missing_sounds:
            print("    ", s)

print("\nTip: Folder names and capitalization must match exactly.")
print("If 'Texture' exists but 'textures' is missing, rename the folder to 'textures'.")
