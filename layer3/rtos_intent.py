from dataclasses import dataclass
from typing import Optional


@dataclass
class RTOSExecutionIntent:
    board: str
    source_root: str

    wrapper_generated: bool
    wrapper_root: Optional[str]

    timeout_ms: int