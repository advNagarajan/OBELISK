import sys
from pathlib import Path
from pprint import pprint

# ---- Add project root to Python path ----
OBELISK_ROOT = Path(r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK")
sys.path.insert(0, str(OBELISK_ROOT))

from layer1.ingest import ingest
from layer2.analyze import analyze
from layer3.synthesize import synthesize
from layer4.run import run_layer4


def test(path):
    print("\n==============================")
    print("TESTING:", path)
    print("==============================")

    # Layer 1 → 3
    artifact = ingest(path)
    system_profile = analyze(artifact)
    plans = synthesize(system_profile)

    print("\n--- Launch Plans ---")
    for p in plans:
        pprint(p)

    # Layer 4
    profiles = run_layer4(plans)

    print("\n--- Execution Profiles ---")
    for prof in profiles:
        pprint(prof)


if __name__ == "__main__":
    inputs = [
        r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK\obelisk_layer_tests\raw_inputs\freedos.boot.disk.160K.img",
        r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK\obelisk_layer_tests\raw_inputs\Win95.iso",
        r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK\obelisk_layer_tests\raw_inputs\DOOM.exe",
    ]

    for p in inputs:
        test(p)
