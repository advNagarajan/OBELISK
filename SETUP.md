# OBELISK Setup Guide

Quick setup guide for the OBELISK framework.

---

## Requirements

- **OS**: Windows 10/11
- **RAM**: 8+ GB
- **Storage**: 20 GB free
- **Admin Access**: Required for emulator installations

---

## Quick Setup

### 1. Install Core Tools

```powershell
# Python 3.10+
winget install Python.Python.3.10

# QEMU (download from qemu.org, install to C:\Program Files\qemu\)
# DOSBox (download from dosbox.com)
```

### 2. Enable WSL2 (for Linux support)

```powershell
wsl --install
# Restart if prompted, then:
wsl
sudo apt update && sudo apt upgrade -y
```

### 3. Setup Linux Runtime (in WSL)

```bash
cd /mnt/c/path/to/obelisk

# Create directories
mkdir -p runtime/linux/alpine_root

# Download and extract Alpine base
cd runtime/linux
wget https://dl-cdn.alpinelinux.org/alpine/v3.18/releases/x86_64/alpine-minirootfs-3.18.0-x86_64.tar.gz
tar -xzf alpine-minirootfs-3.18.0-x86_64.tar.gz -C alpine_root/

# Get Linux kernel
wget https://dl-cdn.alpinelinux.org/alpine/v3.18/main/x86_64/linux-virt-6.1.38-r1.apk
tar -xzf linux-virt-6.1.38-r1.apk
cp boot/vmlinuz-virt ./vmlinuz-virt
```

### 4. Configure Paths

Edit `config.py`:

```python
DOSBOX_PATH = r"C:\Program Files (x86)\DOSBox-0.74-3\DOSBox.exe"
QEMU_PATH = r"C:\Program Files\qemu\qemu-system-i386.exe"
FREEDOS_IMG = r"D:/obelisk_runtime/dos.img"  # Optional, for QEMU DOS
ZEPHYR_BASE_PATH = r"D:\zephyrproject\zephyr"  # Optional, for RTOS
```

### 5. Test

```powershell
# DOS artifact
python main.py input/dos/Nibbles

# Linux artifact
python main.py input/linux/filesystem
```

---

## Optional: Zephyr RTOS Support

```powershell
winget install Kitware.CMake
winget install Ninja-build.Ninja
pip install west
```

Follow [Zephyr Getting Started](https://docs.zephyrproject.org/latest/develop/getting_started/)

---

## Optional: FreeDOS for QEMU

```bash
qemu-img create -f raw D:\obelisk_runtime\dos.img 500M
qemu-system-i386 -hda D:\obelisk_runtime\dos.img -boot d -cdrom FD13-LiveCD.iso
```

---

## Troubleshooting

**"QEMU not found"**: Add `C:\Program Files\qemu` to PATH or update `config.py`

**"Alpine root not found"**: Must be at `runtime/linux/alpine_root/` in project directory

**"Kernel not found"**: Must be at `runtime/linux/vmlinuz-virt`

**WSL build fails**: Run `wsl --update`, verify alpine_root exists

**Permission errors**: Run as Administrator

---

## Checklist

- [ ] Python 3.10+ installed
- [ ] QEMU installed  
- [ ] DOSBox installed
- [ ] WSL2 enabled
- [ ] `runtime/linux/alpine_root/` populated
- [ ] `runtime/linux/vmlinuz-virt` present
- [ ] `config.py` paths updated
- [ ] Test successful

---

**Last Updated**: March 2026 | [GitHub](https://github.com/advNagarajan/obelisk)
