import sys
from pathlib import Path
import json

# --------------------------------------------------
# Make project importable
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from layer2.models import (
    SystemProfile,
    PlatformCandidate,
    EntryPoint,
    SoundProfile,
)

from layer3.synthesize import synthesize


def fake_program_profile(tmp_path: Path) -> SystemProfile:
    return SystemProfile(
        artifact_root=str(tmp_path),

        platform_candidates=[
            PlatformCandidate("dos", 0.9),
        ],

        cpu_class={"minimum": "286", "confidence": 0.8},
        memory_model="real",

        graphics=["text"],
        sound=SoundProfile(
            requirement="optional",
            supported_devices=[],
            confidence=0.3,
            evidence=[]
        ),

        graphics_evidence=[],
        sound_evidence=[],

        entry_points=[
            EntryPoint("GAME.EXE", 0.9)
        ],

        constraints={},
        negative_constraints=[],

        evidence={},
        execution_evidence={},

        execution_surface="program"
    )


# --------------------------------------------------
# Manual runner (prints JSONs)
# --------------------------------------------------
if __name__ == "__main__":
    artifact_dir = PROJECT_ROOT / "artifacts" / "layer3_test_artifact"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    profile = fake_program_profile(artifact_dir)
    plans = synthesize(profile)

    print("\n=== LAYER 3 LAUNCH PLANS ===")
    for plan in plans:
        print(f"- {plan.emulator} | {plan.variant} | priority={plan.priority}")

    print("\n=== QEMU JSON CONFIGS ===")
    for plan in plans:
        if plan.emulator == "qemu":
            cfg_path = Path(plan.config_path)
            print(f"\n--- {cfg_path} ---")
            with open(cfg_path, "r", encoding="utf-8") as f:
                print(json.dumps(json.load(f), indent=2))

    print("\nDone.")
