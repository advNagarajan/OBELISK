import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#V1.0 - Layer 1 (Artifact Extraction)

from layer1.ingest import ingest
from dataclasses import asdict
import json

artifact = ingest("input/DoomTest2")
artifact_dict = asdict(artifact)
with open("artifact_descriptor.txt", "w", encoding="utf-8") as f:
    json.dump(artifact_dict, f, indent=2)

print("Artifact descriptor written to artifact_descriptor.txt")

#V2.0 - Layer 2 (System Inference)

from layer2.analyze import analyze

profile = analyze(artifact)
output = json.dumps(asdict(profile), indent=2)

with open("artifact_profile.txt", "w", encoding="utf-8") as f:
    f.write(output)
print("Possible configuration written to artifact_profile.txt")

print(output)

# V3.0 – Layer 3 (Configuration Synthesis)

from layer3.synthesize import synthesize

plans = synthesize(profile)   # List[LaunchPlan]

layer3_output = [
    asdict(plan) for plan in plans
]


# V4.0 – Filter QEMU plans + run Layer 4

from layer4.run import run_layer4

# Filter QEMU plans
qemu_plans = [p for p in plans if p.emulator == "qemu"]
assert qemu_plans, "No QEMU plans generated"

# Prefer program-minimal if available
selected_plan = None
for p in qemu_plans:
    if p.variant == "program-minimal":
        selected_plan = p
        break

# Fallback: highest priority QEMU plan
if selected_plan is None:
    selected_plan = sorted(qemu_plans, key=lambda p: p.priority)[0]

print("\n=== Selected QEMU Plan ===")
print(f"Variant     : {selected_plan.variant}")
print(f"Config path : {selected_plan.config_path}")
print(f"Priority    : {selected_plan.priority}")

# Run Layer 4 with exactly ONE plan
profiles = run_layer4([selected_plan])

print("\n=== Execution Profile ===")
print(profiles[0])