import sys
from pathlib import Path
import pprint

# -------------------------------------------------
# Path bootstrap
# -------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# -------------------------------------------------
# Imports
# -------------------------------------------------
from layer1.ingest import ingest
from layer2.analyze import analyze
from layer3.synthesize import synthesize

pp = pprint.PrettyPrinter(indent=2)

# -------------------------------------------------
# Artifact under test
# -------------------------------------------------
ARTIFACT_ROOT = ROOT / "artifacts" / "linux_script"

print("\n==============================")
print("OBELISK Linux Script L1–L3 Test")
print("==============================\n")

print("[TEST] Artifact root:", ARTIFACT_ROOT)

# -------------------------------------------------
# Layer 1 — Scan
# -------------------------------------------------
print("\n--- Layer 1: scan_artifact ---\n")

artifact = ingest(ARTIFACT_ROOT)

print("[L1] Artifact object:")
pp.pprint(artifact.__dict__)

# -------------------------------------------------
# Layer 2 — Analyze
# -------------------------------------------------
print("\n--- Layer 2: analyze_artifact ---\n")

system_profile = analyze(artifact)

print("[L2] SystemProfile:")
pp.pprint(system_profile.__dict__)

print("\n[L2] execution_surface =", system_profile.execution_surface)
print("[L2] entry_points =", system_profile.entry_points)
print("[L2] linux_execution_contract =")
pp.pprint(system_profile.linux_execution_contract)

# -------------------------------------------------
# Layer 3 — Synthesize
# -------------------------------------------------
print("\n--- Layer 3: synthesize_launch_plans ---\n")

plans = synthesize(system_profile)

print(f"[L3] Generated {len(plans)} LaunchPlan(s)\n")

for i, plan in enumerate(plans):
    print(f"[L3] LaunchPlan #{i}")
    pp.pprint(plan.__dict__)
    print()

print("\n==============================")
print("END OF L1–L3 TEST")
print("==============================\n")
