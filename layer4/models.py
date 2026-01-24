from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum

class ExecutionMode(Enum):
    PROCESS = "process"
    SYSTEM = "system"

@dataclass
class ExecutionProfile:
    # Identity
    emulator: str
    variant: str
    entry_point: Optional[str]

    # Execution model (CRITICAL)
    execution_mode: ExecutionMode

    # Execution phases (facts derived from sentinels + time)
    phases: Dict[str, bool]

    # Ground-truth execution evidence (OS-level)
    sentinels: Dict[str, Optional[int]]

    # Configuration metadata (input, not inference)
    config: Dict[str, str]

    # Sound stuff
    sound_outcome: Optional[str]

    # Optional diagnostics (non-semantic)
    host_telemetry: Dict[str, object]
