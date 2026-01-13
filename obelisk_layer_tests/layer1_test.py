import sys
print(sys.path[0])

from pathlib import Path
import json
from dataclasses import asdict

# 👇 POINT TO *INNER* obelisk folder (the one with layer1/)
OBELISK_ROOT = Path(r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK")
sys.path.insert(0, str(OBELISK_ROOT))

from layer1.ingest import ingest
def test(path):
    artifact = ingest(path)
    print(json.dumps(asdict(artifact), indent=2))

if __name__ == "__main__":
    test(r"C:\Users\Aadhav Nagarajan\OneDrive\Desktop\OBELISK\obelisk_layer_tests\raw_inputs\freedos.boot.disk.160K.img")
