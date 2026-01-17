from dataclasses import dataclass

@dataclass
class LaunchPlan:
    emulator: str
    config_path: str
    artifact_root: str
    entry_point: str | None

    fallback_timeout: int  # used only if config omits timeout
    confidence: float
    variant: str
    priority: int