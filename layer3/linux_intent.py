from dataclasses import dataclass
from typing import List, Dict

@dataclass
class LinuxExecutionIntent:
    kernel_path: str
    initramfs_path: str

    exec_path: str          # e.g. /bin/busybox
    exec_args: List[str]    # e.g. ["sh", "/artifact/script.sh"]

    memory_mb: int
    timeout_ms: int

    console: str            # "serial"
    graphics: str           # "none"

    env: Dict[str, str]
