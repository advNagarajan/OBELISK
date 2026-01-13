from dataclasses import dataclass
from typing import List, Literal

@dataclass
class CanonicalMachine:
    """
    Emulator-agnostic description of the minimum viable machine.
    """
    cpu: Literal["8086", "286", "386", "486"]
    memory_mb: int
    graphics: Literal["text", "vga", "svga"]

    sound: List[str]
    sound_required: bool

    dos_extender: bool
