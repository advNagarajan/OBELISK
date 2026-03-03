# layer5/models.py

from dataclasses import dataclass
from typing import Dict, List, Optional


# ============================================================
# Core Observation
# ============================================================

@dataclass
class ExecutionObservation:
    """
    Normalized, emulator-agnostic view of one execution attempt.
    Conservative interpretation of Layer 4 signals.
    """

    emulator: str
    variant: str
    entry_point: Optional[str]

    execution_class: str      # stable | partial | failed
    stable: bool              # convenience flag

    features: Dict[str, object]
    sound_outcome: Optional[str]

    host_telemetry: Dict[str, object]


# ============================================================
# Inference Output
# ============================================================

@dataclass
class InferredRequirement:
    feature: str
    status: str               # required | optional | forbidden | preferred | unknown
    confidence: float
    evidence: List[str]
    preferred_value: object = None


# ============================================================
# Evaluation / Ranking
# ============================================================

@dataclass
class EvaluatedConfiguration:
    variant: str
    emulator: str
    execution_class: str
    stable: bool
    satisfies_requirements: bool
    score: float
    violations: List[str]


# ============================================================
# Compatibility Metrics
# ============================================================

@dataclass
class CompatibilitySummary:
    total_runs: int
    stable_runs: int
    stability_rate: float


# ============================================================
# Final Layer 5 Result
# ============================================================

@dataclass
class Layer5Result:
    chosen_variant: str
    inferred_requirements: List[InferredRequirement]
    ranked_variants: List[EvaluatedConfiguration]
    compatibility_by_emulator: Dict[str, CompatibilitySummary]
    explanation: str