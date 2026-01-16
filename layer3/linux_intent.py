from dataclasses import dataclass
from typing import Literal, Dict, List

@dataclass
class LinuxExecutionIntent:
    kernel_path: str
    initramfs_path: str

    mode: Literal["init", "program", "boot"]
    entry_point: str              # always "/init"

    memory_mb: int
    timeout_ms: int

    graphics: Literal["none", "framebuffer"]
    console: Literal["serial"]

    env: Dict[str, str]
    arguments: List[str]
