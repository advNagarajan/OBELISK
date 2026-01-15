import subprocess
from pathlib import Path
import tempfile
import shutil

# -----------------------------
# Fixed paths (runtime base)
# -----------------------------
QEMU = r"C:\Program Files\qemu\qemu-system-i386.exe"
DOS_IMG = Path("D:/obelisk_runtime/dos.img")

DOOM_SRC = Path("D:/obelisk_runtime/inputs/DoomTest2")

CPU = "qemu32"
MEM_MB = 16

# -----------------------------
# Sanity checks
# -----------------------------
if not DOS_IMG.exists():
    raise FileNotFoundError("dos.img not found (base image must exist)")

if not (DOOM_SRC / "DOOM.EXE").exists():
    raise FileNotFoundError("DOOM.EXE missing")

if not (DOOM_SRC / "DOOM1.WAD").exists():
    raise FileNotFoundError("DOOM1.WAD missing")

# -----------------------------
# Create per-run C: drive
# -----------------------------
with tempfile.TemporaryDirectory() as tmp:
    run_dir = Path(tmp)

    # Copy program files
    shutil.copy(DOOM_SRC / "DOOM.EXE", run_dir)
    shutil.copy(DOOM_SRC / "DOOM1.WAD", run_dir)

    # Generate AUTOEXEC.BAT
    autoexec = run_dir / "AUTOEXEC.BAT"
    autoexec.write_text(
        "@ECHO OFF\n"
        "C:\n"
        "DOOM.EXE\n"
    )

    # -----------------------------
    # Launch QEMU
    # -----------------------------
    subprocess.run([
        QEMU,
        "-cpu", CPU,
        "-m", str(MEM_MB),
        "-drive", f"file={DOS_IMG.as_posix()},format=raw,if=ide",
        "-drive", f"file=fat:rw:{run_dir.as_posix()},format=raw",
        "-boot", "c",
        "-vga", "std",
        "-no-reboot",
    ])
