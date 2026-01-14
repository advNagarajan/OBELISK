import os
import subprocess
from pathlib import Path

# -----------------------------
# Resolve base paths safely
# -----------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DOS_IMG = SCRIPT_DIR / "dos.img"
FREEDOS_ISO = SCRIPT_DIR / "freedos" / "FD14LGCY.iso"
DOOM_DIR = PROJECT_ROOT / "input" / "DoomTest2"

QEMU = r"C:\Program Files\qemu\qemu-system-i386.exe"
QEMU_IMG = r"C:\Program Files\qemu\qemu-img.exe"

# -----------------------------
# Sanity checks
# -----------------------------
if not FREEDOS_ISO.exists():
    raise FileNotFoundError(f"FreeDOS ISO not found: {FREEDOS_ISO}")

if not (DOOM_DIR / "DOOM.EXE").exists():
    raise FileNotFoundError("DOOM.EXE not found in input/")

if not (DOOM_DIR / "DOOM1.WAD").exists():
    raise FileNotFoundError("DOOM1.WAD not found in input/")

# -----------------------------
# Step 1: Create empty disk image
# -----------------------------
if not DOS_IMG.exists():
    subprocess.run(
        [QEMU_IMG, "create", "-f", "raw", str(DOS_IMG), "200M"],
        check=True
    )

# -----------------------------
# Step 2: Install FreeDOS (manual, once)
# -----------------------------
FREEDOS_MARKER = SCRIPT_DIR / ".freedos_installed"

if not FREEDOS_MARKER.exists():
    print("=== Install FreeDOS into dos.img ===")
    print("Follow installer steps, then EXIT QEMU.")

    subprocess.run([
        QEMU,
        "-cpu", "qemu32",
        "-m", "16",
        "-hda", str(DOS_IMG),
        "-cdrom", str(FREEDOS_ISO),
        "-boot", "d",
        "-vga", "std"
    ])

    input("\nPress Enter AFTER FreeDOS installation is complete...")
    FREEDOS_MARKER.touch()
else:
    print("FreeDOS already installed, skipping installer.")

# -----------------------------
# Step 3: Copy DOOM using mtools
# -----------------------------
# Requires mtools (mcopy, mmd) to be installed

MMD = r"C:\msys64\mingw64\bin\mmd.exe"
MCOPY = r"C:\msys64\mingw64\bin\mcopy.exe"
IMG = f"{DOS_IMG}@@1"

subprocess.run([MMD, "-i", IMG, "::/DOOM"], check=True)

subprocess.run([
    MCOPY, "-i", IMG,
    str(DOOM_DIR / "DOOM.EXE"),
    "::/DOOM/"
], check=True)

subprocess.run([
    MCOPY, "-i", IMG,
    str(DOOM_DIR / "DOOM1.WAD"),
    "::/DOOM/"
], check=True)

# -----------------------------
# Step 4: Create AUTOEXEC.BAT
# -----------------------------
autoexec_content = """@ECHO OFF
C:
CD \\DOOM
DOOM.EXE
"""

autoexec_path = SCRIPT_DIR / "AUTOEXEC.BAT"
autoexec_path.write_text(autoexec_content)

subprocess.run([
    MCOPY, "-i", IMG,
    str(autoexec_path),
    "::/AUTOEXEC.BAT"
], check=True)

print("=== DOOM installed successfully ===")

# -----------------------------
# Step 5: Launch DOOM
# -----------------------------
subprocess.run([
    QEMU,
    "-cpu", "qemu32",
    "-m", "16",
    "-hda", str(DOS_IMG),
    "-boot", "c",
    "-vga", "std",
    "-soundhw", "none",
    "-no-reboot"
])
