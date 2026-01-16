import sys
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from layer1.ingest import ingest
from layer2.analyze import analyze

TEST_ROOT = "obelisk_layer_tests/obelisk_layer1_tests"

tests = {
    "hello": "Single ELF",
    "test.sh": "Shell script",
    "linux_artifact": "Linux initramfs-style artifact",
    "DoomTest2": "DOS Program"
}

for name, label in tests.items():
    print("=" * 70)
    print(label)
    print("Input:", name)

    artifact = ingest(f"{TEST_ROOT}/{name}")
    profile = analyze(artifact)

    print("Platform candidates:")
    for p in profile.platform_candidates:
        print(" ", p)

    print("Execution surface:", profile.execution_surface)

    print("Entry points:")
    for e in profile.entry_points:
        print(" ", e)

    print("Negative constraints:", profile.negative_constraints)
