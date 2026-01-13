import sys
from pathlib import Path
import json

# --------------------------------------------------
# Make project root importable
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from layer2.models import (
    SystemProfile,
    PlatformCandidate,
    SoundProfile
)

from layer3.synthesize import synthesize


# --------------------------------------------------
# Fake Layer-2 output: NON-DOS, bootable artifact
# --------------------------------------------------

def fake_nondos_boot_profile(tmp_path: Path) -> SystemProfile:
    """
    Simulates a bootable, non-DOS artifact
    (e.g., installer ISO, unknown OS, legacy OS).
    """

    return SystemProfile(
        artifact_root=str(tmp_path),

        platform_candidates=[
            PlatformCandidate("unknown", 0.7),
            PlatformCandidate("dos", 0.1),
        ],

        cpu_class={"minimum": "386", "confidence": 0.6},
        memory_model="protected",

        graphics=["text"],

        sound=SoundProfile(
            requirement="absent",
            supported_devices=[],
            confidence=0.9,
            evidence=[]
        ),

        graphics_evidence=[],
        sound_evidence=[],

        entry_points=[],  # 🚨 no executable entry point

        constraints={},
        negative_constraints=["not_dos"],

        evidence={},
        execution_evidence={},

        execution_surface="boot_disk"
    )


# --------------------------------------------------
# Manual runner
# --------------------------------------------------

if __name__ == "__main__":
    artifact_dir = PROJECT_ROOT / "artifacts" / "layer3_nondos_test"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    profile = fake_nondos_boot_profile(artifact_dir)
    plans = synthesize(profile)

    print("\n=== LAYER 3 NON-DOS LAUNCH PLANS ===")

    for plan in plans:
        print(
            f"- {plan.emulator} | {plan.variant} | priority={plan.priority}"
        )

    print("\n=== ASSERTIONS ===")

    emulators = {p.emulator for p in plans}

    print("Emulators seen:", emulators)

    assert "dosbox" not in emulators, "❌ DOSBox should NOT appear"
    assert "qemu" in emulators, "❌ QEMU should appear"

    for plan in plans:
        assert plan.entry_point == "", "❌ Boot plan must not have entry point"

        cfg = Path(plan.config_path)
        assert cfg.exists(), f"❌ Missing config file: {cfg}"

        with open(cfg, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["execution"]["mode"] == "boot_disk"

    print("\n✅ NON-DOS Layer 3 test PASSED")
