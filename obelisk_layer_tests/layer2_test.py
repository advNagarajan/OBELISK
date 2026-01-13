import sys
from pathlib import Path
import os

OBELISK_ROOT = Path(r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK")
sys.path.insert(0, str(OBELISK_ROOT))

from layer1.ingest import ingest
from layer2.analyze import analyze
from pprint import pprint


def test(path):
    print("PATH:", path)
    print("  exists :", os.path.exists(path))
    print("  isfile :", os.path.isfile(path))
    print("  isdir  :", os.path.isdir(path))

    artifact = ingest(path)
    profile = analyze(artifact)
    pprint(profile)

if __name__ == "__main__":
    inputs = [
        r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK\obelisk_layer_tests\raw_inputs\freedos.boot.disk.160K.img",
        r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK\obelisk_layer_tests\raw_inputs\Win95.iso",
        r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK\obelisk_layer_tests\raw_inputs\DOOM.exe",
        r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK\obelisk_layer_tests\raw_inputs\archive.zip",
    ]



    for p in inputs:
        print("\n=== TESTING:", p, "===")
        test(p)