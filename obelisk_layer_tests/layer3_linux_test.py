import sys
from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

"""
Manual inspection script for Layer 3 profile selection.

This script prints synthesized LaunchPlans for visual verification.
It performs NO assertions and must not be used as a test gate.
"""

from layer3.synthesize import synthesize
from layer2.models import SystemProfile, PlatformCandidate, EntryPoint


def dump_plans(label, plans):
    print("=" * 70)
    print(label)
    print("=" * 70)

    if not plans:
        print("NO PLANS PRODUCED")
        return

    for i, plan in enumerate(plans, 1):
        print(f"Plan #{i}")
        print(f"  emulator      : {plan.emulator}")
        print(f"  variant       : {plan.variant}")
        print(f"  entry_point   : {plan.entry_point}")
        print(f"  artifact_root : {plan.artifact_root}")
        print(f"  priority      : {plan.priority}")
        print(f"  confidence    : {plan.confidence}")
        print()


def linux_program_case():
    profile = SystemProfile(
        artifact_root="artifacts/hello",

        platform_candidates=[
            PlatformCandidate(platform="linux", confidence=0.95)
        ],

        cpu_class={},
        memory_model="protected",

        graphics=[],
        sound=None,

        graphics_evidence=[],
        sound_evidence=[],

        entry_points=[],

        constraints={},
        negative_constraints=["not_dos", "not_windows"],

        evidence={},
        execution_evidence={},

        execution_surface="linux_program"
    )

    plans = synthesize(profile)
    dump_plans("LINUX PROGRAM (ELF / SCRIPT)", plans)


def linux_init_case():
    profile = SystemProfile(
        artifact_root="artifacts/linux_artifact",

        platform_candidates=[
            PlatformCandidate(platform="linux", confidence=0.95)
        ],

        cpu_class={},
        memory_model="protected",

        graphics=[],
        sound=None,

        graphics_evidence=[],
        sound_evidence=[],

        entry_points=[
            EntryPoint(path="init", confidence=0.9)
        ],

        constraints={},
        negative_constraints=["not_dos", "not_windows"],

        evidence={},
        execution_evidence={},

        execution_surface="linux_init"
    )

    plans = synthesize(profile)
    dump_plans("LINUX INITRAMFS ARTIFACT", plans)


def dos_case():
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
    dump_plans("DOS PROGRAM (REGRESSION CHECK)", plans)


if __name__ == "__main__":
    linux_program_case()
    linux_init_case()
    dos_case()
