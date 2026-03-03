"""
OBELISK Test Harness
Layer-isolated execution with clear failure reporting.
"""

import sys
import json
import traceback
from pathlib import Path
from dataclasses import asdict
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

DEFAULT_ARTIFACT = "input/hello_world"   # change as needed


def banner(title):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def fail(layer_name, e):
    print(f"\n❌ FAILURE in {layer_name}")
    print("-" * 70)
    traceback.print_exc()
    print("-" * 70)
    sys.exit(1)


def main():

    artifact_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ARTIFACT

    banner("LAYER 1 — INGEST")

    try:
        from layer1.ingest import ingest
        artifact = ingest(artifact_path)

        artifact_dict = asdict(artifact)

        with open("artifact_descriptor.json", "w", encoding="utf-8") as f:
            json.dump(artifact_dict, f, indent=2)

        print("✔ Artifact ingested")
        print("Descriptor written to artifact_descriptor.json")

    except Exception as e:
        fail("LAYER 1 (INGEST)", e)

    # -------------------------------------------------

    banner("LAYER 2 — ANALYZE")

    try:
        from layer2.analyze import analyze

        profile = analyze(artifact)

        profile_dict = asdict(profile)

        with open("artifact_profile.json", "w", encoding="utf-8") as f:
            json.dump(profile_dict, f, indent=2)

        print("✔ System profile generated")
        print("Profile written to artifact_profile.json")

        print("\nExecution surface:", profile.execution_surface)

    except Exception as e:
        fail("LAYER 2 (ANALYZE)", e)

    # -------------------------------------------------

    banner("LAYER 3 — SYNTHESIZE")

    try:
        from layer3.synthesize import synthesize

        plans = synthesize(profile)

        layer3_output = [asdict(plan) for plan in plans]

        with open("artifact_launch_plans.json", "w", encoding="utf-8") as f:
            json.dump(layer3_output, f, indent=2)

        print("✔ Launch plans synthesized")
        print("Launch plans written to artifact_launch_plans.json")

        print("\nGenerated Launch Plans:")
        for plan in plans:
            print(
                f"- variant={plan.variant:20} "
                f"priority={plan.priority:<2} "
                f"emulator={plan.emulator:<8} "
                f"entry={plan.entry_point}"
            )

        if not plans:
            print("\n⚠ No launch plans generated.")
            sys.exit(1)

    except Exception as e:
        fail("LAYER 3 (SYNTHESIZE)", e)

    # -------------------------------------------------

    banner("LAYER 4 — EXECUTION")

    try:
        from layer4.run import run_layer4

        execution_profiles = run_layer4(plans)

        out_dir = Path("layer4_output")
        out_dir.mkdir(exist_ok=True)

        print("\nExecution Profiles:\n")

        for exec_profile in execution_profiles:

            print("TYPE:", type(exec_profile))

            if exec_profile.host_telemetry.get("interactive"):
                print("Interactive mode — no stdout captured.")
            else:
                print("STDOUT SAMPLE:")
                print(exec_profile.host_telemetry.get("stdout_sample"))

            profile_dict = asdict(exec_profile)

            # convert enums to string
            for k, v in profile_dict.items():
                if hasattr(v, "name"):
                    profile_dict[k] = v.name

            print(json.dumps(profile_dict, indent=2))

        print("\n✔ Layer 4 execution completed")

    except Exception as e:
        fail("LAYER 4 (EXECUTION)", e)


if __name__ == "__main__":
    main()