from pathlib import Path
import sys

# -------------------------------------------------
# Path bootstrap
# -------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# L3
from layer3.synthesize import synthesize

# L4
from layer4.run import run_layer4


def main():
    # ------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------
    project_root = ROOT
    artifact_root = project_root / "artifacts" / "abcdefg"

    if not artifact_root.exists():
        raise FileNotFoundError(
            f"Expected artifact directory at {artifact_root}"
        )

    # ------------------------------------------------------------------
    # Construct SystemProfile (THIS IS L2 OUTPUT)
    # ------------------------------------------------------------------
    system_profile = type("SystemProfile", (), {})()

    # Identity
    system_profile.artifact_root = str(artifact_root)

    # Platform inference (L2 already knows this is Linux)
    system_profile.platform_candidates = [
        {"platform": "linux", "confidence": 1.0}
    ]

    # CPU & execution model
    system_profile.cpu_class = {}
    system_profile.memory_model = "protected"

    # Conservative assertions
    system_profile.graphics = []
    system_profile.sound = False

    # Evidence-only
    system_profile.graphics_evidence = []
    system_profile.sound_evidence = []

    # Entry points (not used for Linux boot model)
    system_profile.entry_points = []

    # Constraints
    system_profile.constraints = {}
    system_profile.negative_constraints = []

    # Raw evidence
    system_profile.evidence = {}
    system_profile.execution_evidence = {}

    # 🔹 L2 ASSERTION: this is a Linux execution surface
    system_profile.execution_surface = "linux_contract"

    system_profile.linux_execution_contract =  {
            "interface": "exec+args",
            "executor": "init"
        }

    # IMPORTANT:
    # No linux_execution_contract
    # No JSON
    # L3 must infer + emit everything itself

    # ------------------------------------------------------------------
    # L3 synthesis → LaunchPlans
    # ------------------------------------------------------------------
    plans = synthesize(system_profile)

    print(f"[TEST] L3 synthesized {len(plans)} plan(s)")
    for p in plans:
        print(p)

    # ------------------------------------------------------------------
    # L4 execution
    # ------------------------------------------------------------------
    profiles = run_layer4(plans)

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------
    print("\n[TEST] Execution profiles:")
    for i, profile in enumerate(profiles):
        print(f"\n--- Profile {i} ---")
        print(profile)

    print("\n[TEST] Layer 3 → Layer 4 Linux integration test complete")


if __name__ == "__main__":
    main()
