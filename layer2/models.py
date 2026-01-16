from dataclasses import dataclass
from typing import List, Dict, Literal


# --------------------------------------
# Platform likelihoods
# --------------------------------------

@dataclass
class PlatformCandidate:
    platform: str          # "dos", "windows", "unknown"
    confidence: float      # 0.0 – 1.0


# --------------------------------------
# Entry points
# --------------------------------------

@dataclass
class EntryPoint:
    path: str
    confidence: float      # likelihood this is a primary entry point


# --------------------------------------
# Final Layer-2 output
# --------------------------------------

@dataclass
class SoundProfile:
    requirement: Literal["required", "optional", "absent"]
    supported_devices: List[str]
    confidence: float
    evidence: List[str]

@dataclass
class SystemProfile:
    # Identity
    artifact_root: str 

    # Platform inference
    platform_candidates: List[PlatformCandidate]

    # CPU & execution model
    cpu_class: Dict
    memory_model: Literal["real", "protected", "unknown"]

    # Conservative assertions
    graphics: List[str]
    sound: SoundProfile

    # Evidence-only (non-binding)
    graphics_evidence: List[str]
    sound_evidence: List[str]

    # Entry points (if applicable)
    entry_points: List[EntryPoint]

    # Hard / negative constraints
    constraints: Dict[str, bool]
    negative_constraints: List[str]

    # Raw evidence (audit trail)
    evidence: Dict[str, list]

    # Execution-relevant evidence (backend-usable)
    execution_evidence: Dict[str, list]

    # 🔹 NEW: execution surface (ties to Layer 1)
    execution_surface: Literal[
        "boot_disk",
        "dos_program",
        "linux_init",
        "linux_program",
        "unknown"
    ]
