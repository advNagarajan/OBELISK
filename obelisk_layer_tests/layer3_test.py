import sys
from pathlib import Path
from pprint import pprint

OBELISK_ROOT = Path(r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK")
sys.path.insert(0, str(OBELISK_ROOT))

from layer1.ingest import ingest
from layer2.analyze import analyze
from layer3.synthesize import synthesize


def test(path):
    artifact = ingest(path)
    profile = analyze(artifact)
    plans = synthesize(profile)

    print("\n=== ARTIFACT ===")
    print(path)
    print("execution_mode:", profile.execution_mode)

    print("\n=== LAUNCH PLANS ===")
    for p in plans:
        pprint(p)

    assert not (
        profile.execution_mode == "bootable_os"
        and any(p.emulator == "dosbox" for p in plans)
    )


if __name__ == "__main__":
    inputs = [
        r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK\obelisk_layer_tests\raw_inputs\freedos.boot.disk.160K.img",
        r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK\obelisk_layer_tests\raw_inputs\Win95.iso",
        r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK\obelisk_layer_tests\raw_inputs\DOOM.exe",
        r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK\obelisk_layer_tests\raw_inputs\archive.zip",
    ]

    for p in inputs:
        test(p)
