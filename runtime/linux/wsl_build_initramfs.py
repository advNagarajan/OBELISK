import sys
import shutil
import subprocess
from pathlib import Path

# Arguments:
#   argv[1] = alpine_root (WSL-visible path)
#   argv[2] = artifact_root (WSL-visible path)
#   argv[3] = artifact entrypoint (e.g. test.sh)
#   argv[4] = output initramfs path (WSL-visible path)

if len(sys.argv) != 5:
    print(
        "Usage: wsl_build_initramfs.py "
        "<alpine_root> <artifact_root> <entrypoint> <output_initramfs>"
    )
    sys.exit(1)

alpine_root = Path(sys.argv[1])
artifact_root = Path(sys.argv[2])
entrypoint = sys.argv[3]
output_initramfs = Path(sys.argv[4])

# Native WSL workspace (CRITICAL)
base_root = Path("/tmp/obelisk_base_root")
tmp_initramfs = Path("/tmp/obelisk_initramfs.img")

# --- Validation ---
if not alpine_root.exists():
    print(f"ERROR: alpine_root not found: {alpine_root}")
    sys.exit(1)

if not artifact_root.exists():
    print(f"ERROR: artifact_root not found: {artifact_root}")
    sys.exit(1)

artifact_entry = artifact_root / entrypoint
if not artifact_entry.exists():
    print(f"ERROR: artifact entrypoint not found: {artifact_entry}")
    sys.exit(1)

# --- Clean workspace ---
if base_root.exists():
    shutil.rmtree(base_root)

base_root.mkdir(parents=True)

print("[WSL] Copying Alpine donor filesystem...")
shutil.copytree(
    alpine_root,
    base_root,
    symlinks=True,
    dirs_exist_ok=True,
)

# --- Embed artifact ---
print("[WSL] Embedding artifact...")
artifact_dst = base_root / "artifact"
artifact_dst.mkdir()

for item in artifact_root.iterdir():
    if item.is_file():
        shutil.copy(item, artifact_dst / item.name)

(artifact_dst / entrypoint).chmod(0o755)

# --- Install OBELISK init ---
print("[WSL] Installing OBELISK init...")

init_script = f"""#!/bin/sh
echo "OBELISK: custom init starting"

# --- Basic system setup ---
/bin/busybox mkdir -p /proc /sys /dev
/bin/busybox mount -t proc proc /proc
/bin/busybox mount -t sysfs sysfs /sys
/bin/busybox mount -t devtmpfs devtmpfs /dev

/bin/busybox --install -s /bin
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
mdev -s

echo "OBELISK: starting artifact execution"

ARTIFACT="/artifact/{entrypoint}"

if [ ! -x "$ARTIFACT" ]; then
    echo "OBELISK ERROR: artifact not executable: $ARTIFACT"
    exec sh
fi

echo "OBELISK: exec $ARTIFACT"
setsid "$ARTIFACT" </dev/tty0 >/dev/tty0 2>&1
RC=$?

echo "OBELISK: artifact exited with code $RC"
echo "OBELISK: entering idle state"
exec sleep infinity
"""

init_path = base_root / "init"
init_path.write_text(init_script, newline="\n")
init_path.chmod(0o755)

# --- Pack initramfs ---
print("[WSL] Packing initramfs...")

if tmp_initramfs.exists():
    tmp_initramfs.unlink()

subprocess.run(
    "find . -print | cpio -o -H newc --owner=root:root | gzip > /tmp/obelisk_initramfs.img",
    cwd=base_root,
    shell=True,
    check=True,
)

# --- Copy back to Windows ---
print("[WSL] Copying initramfs to output path...")
print("[WSL DEBUG] Writing initramfs to:", output_initramfs)
output_initramfs.parent.mkdir(parents=True, exist_ok=True)
shutil.copy(tmp_initramfs, output_initramfs)

print("[WSL] initramfs generated successfully:", output_initramfs)
