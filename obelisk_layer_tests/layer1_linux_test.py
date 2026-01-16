import sys
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from layer1.ingest import ingest

TEST_ROOT = os.path.join(
    "obelisk_layer_tests",
    "obelisk_layer1_tests"
)

tests = [
    "hello",
    "test.sh",
    "linux_artifact",
    "linux_artifact.zip"
]

for t in tests:
    path = os.path.join(TEST_ROOT, t)

    print("=" * 60)
    print("Ingesting:", path)

    desc = ingest(path)
    print(desc)

    for f in desc.files:
        print(" ", f.path, oct(f.mode))