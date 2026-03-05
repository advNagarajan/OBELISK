"""
OBELISK Test Harness
Layer-isolated execution with clear failure reporting.
Now includes Layer 5 (Compatibility + Inference + Selection).
"""

import sys
import json
import traceback
from pathlib import Path
from dataclasses import asdict

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

DEFAULT_ARTIFACT = "input/dos/Wolfenstein3D"   # change as needed


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

    # ============================================================
    # LAYER 1 — INGEST
    # ============================================================

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

    # ============================================================
    # LAYER 2 — ANALYZE
    # ============================================================

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

    # ============================================================
    # LAYER 3 — SYNTHESIZE
    # ============================================================

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

    # ============================================================
    # LAYER 4 — EXECUTION
    # ============================================================

    banner("LAYER 4 — EXECUTION")

    try:
        from layer4.run import run_layer4

        execution_profiles = run_layer4(plans)

        out_dir = Path("layer4_output")
        out_dir.mkdir(exist_ok=True)

        print("\nExecution Profiles:\n")

        serialized_profiles = []

        for exec_profile in execution_profiles:

            profile_dict = asdict(exec_profile)

            # Convert enums to string for JSON safety
            for k, v in profile_dict.items():
                if hasattr(v, "name"):
                    profile_dict[k] = v.name

            serialized_profiles.append(profile_dict)

            print(f"\nVariant: {exec_profile.variant}")
            print("Emulator:", exec_profile.emulator)
            print("Phases:", exec_profile.phases)

        with open(out_dir / "execution_profiles.json", "w", encoding="utf-8") as f:
            json.dump(serialized_profiles, f, indent=2)

        print("\n✔ Layer 4 execution completed")
        print("Execution profiles written to layer4_output/execution_profiles.json")

    except Exception as e:
        fail("LAYER 4 (EXECUTION)", e)

    # ============================================================
    # LAYER 5 — ANALYSIS & COMPATIBILITY
    # ============================================================

    banner("LAYER 5 — ANALYSIS & COMPATIBILITY")

    try:
        from layer5.run import run_layer5

        result = run_layer5(execution_profiles)

        result_dict = asdict(result)

        # Write final result
        with open("artifact_result.json", "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2)

        print("✔ Layer 5 analysis completed")
        print("Final result written to artifact_result.json")

        print("\nChosen Canonical Variant:")
        print("→", result.chosen_variant)

        print("\nCompatibility Summary:")
        for emulator, summary in result.compatibility_by_emulator.items():
            print(
                f"- {emulator}: "
                f"{summary.stable_runs}/{summary.total_runs} stable "
                f"({summary.stability_rate})"
            )

        print("\nExplanation:")
        print(result.explanation)

    except Exception as e:
        fail("LAYER 5 (ANALYSIS)", e)


if __name__ == "__main__":
    main()