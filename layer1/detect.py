MAGIC_BYTES = {
    b"\x7FELF": "elf",
    b"MZ": "exe",
    b"PK\x03\x04": "zip",
    b"\xEB\x3C\x90": "boot_sector",
    b"\x55\xAA": "boot_signature"
}

def detect_shebang(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(2) == b"#!"
    except Exception:
        return False
    
def detect_magic(path: str) -> str:
    try:
        with open(path, "rb") as f:
            header = f.read(4)
        for magic, ftype in MAGIC_BYTES.items():
            if header.startswith(magic):
                return ftype
    except Exception:
        pass
    return "unknown"

def detect_extension(filename: str) -> str:
    name = filename.lower()
    if name.endswith(".exe"):
        return "exe"
    if name.endswith(".com"):
        return "com"
    if name.endswith(".img") or name.endswith(".iso"):
        return "disk_image"
    if name.endswith(".zip"):
        return "zip"
    if name.endswith(".dll"):
        return "dll"
    if name.endswith(".pyd"):
        return "pyd"
    return "unknown"

def detect_file_type(path: str) -> str:
    magic = detect_magic(path)
    if magic != "unknown":
        return magic

    if detect_shebang(path):
        return "script"

    return detect_extension(path)

def detect_bootable(path: str) -> bool:
    """
    Layer 1 definition of bootable:
    The image contains any known firmware boot signature
    within the first bounded region.
    """
    try:
        with open(path, "rb") as f:
            data = f.read(64 * 1024)  # first 64 KB only

        # 1️⃣ BIOS boot sector / MBR signature
        if len(data) >= 512 and data[510:512] == b"\x55\xAA":
            return True

        # 2️⃣ El Torito CD-ROM boot catalog signature
        if b"EL TORITO SPECIFICATION" in data:
            return True

        return False

    except Exception:
        return False


