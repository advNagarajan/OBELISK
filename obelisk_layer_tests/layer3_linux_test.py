"""
Layer 3 Linux synthesis tests for OBELISK Phase 2.5

These tests assert that:
- Linux execution surfaces are handled deterministically
- Exactly one LaunchPlan is produced for Linux
- Entry point semantics are correct
- DOS logic is not regressed

Passing these tests means Linux is CLOSED at Layer 3.
"""
import sys
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from layer3.synthesize import synthesize
from layer2.models import (
    SystemProfile,
    PlatformCandidate,
    EntryPoint
)


def _base_linux_profile(
    *,
    artifact_root: str,
    execution_surface: str,
    entry_points=None
):
    """
    Helper to construct a minimal Linux SystemProfile
    consistent with Phase 2.5 assumptions.
    """
    return SystemProfile(
        artifact_root=artifact_root,

        platform_candidates=[
            PlatformCandidate(platform="linux", confidence=0.95)
        ],

        cpu_class={},                     # Linux abstracts CPU details
        memory_model="protected",

        graphics=[],                      # Non-binding for Phase 2.5
        sound=None,

        graphics_evidence=[],
        sound_evidence=[],

        entry_points=entry_points or [],

        constraints={},
        negative_constraints=["not_dos", "not_windows"],

        evidence={},
        execution_evidence={},

        execution_surface=execution_surface
    )


# ---------------------------------------------------------------------
# TEST 1: Linux ELF / script (linux_program)
# ---------------------------------------------------------------------

def test_layer3_linux_program():
    """
    A single ELF or script artifact should synthesize
    exactly one Linux LaunchPlan with /init as entry point.
    """

    profile = _base_linux_profile(
        artifact_root="artifacts/hello",
        execution_surface="linux_program"
    )

    plans = synthesize(profile)

    assert len(plans) == 1, "Expected exactly one LaunchPlan for linux_program"

    plan = plans[0]
    assert plan.emulator == "qemu"
    assert plan.variant == "linux"
    assert plan.entry_point == "/init"


# ---------------------------------------------------------------------
# TEST 2: Linux initramfs-style artifact (linux_init)
# ---------------------------------------------------------------------

def test_layer3_linux_initramfs():
    """
    An artifact that already provides /init should be
    executed as-is, without synthetic entry points.
    """

    profile = _base_linux_profile(
        artifact_root="artifacts/linux_artifact",
        execution_surface="linux_init",
        entry_points=[
            EntryPoint(path="init", confidence=0.9)
        ]
    )

    plans = synthesize(profile)

    assert len(plans) == 1, "Expected exactly one LaunchPlan for linux_init"

    plan = plans[0]
    assert plan.entry_point == "/init"


# ---------------------------------------------------------------------
# TEST 3: Regression guard — DOS must not trigger Linux logic
# ---------------------------------------------------------------------

def test_layer3_dos_not_linux():
    """
    DOS artifacts must not activate Linux adapters.
    This protects Phase 2 from regression.
    """

    profile = SystemProfile(
        artifact_root="artifacts/DoomTest2",

        platform_candidates=[
            PlatformCandidate(platform="dos", confidence=0.85)
        ],

        cpu_class={"minimum": "386"},
        memory_model="real",

        graphics=["vga"],
        sound=None,

        graphics_evidence=[],
        sound_evidence=[],

        entry_points=[],

        constraints={},
        negative_constraints=["not_linux"],

        evidence={},
        execution_evidence={},

        execution_surface="dos_program"
    )

    plans = synthesize(profile)

    assert all(
        p.variant != "linux" for p in plans
    ), "DOS execution must not produce Linux LaunchPlans"


# ---------------------------------------------------------------------
# Optional manual runner
# ---------------------------------------------------------------------

if __name__ == "__main__":
    test_layer3_linux_program()
    test_layer3_linux_initramfs()
    test_layer3_dos_not_linux()
    print("Layer 3 Linux synthesis tests PASSED.")
