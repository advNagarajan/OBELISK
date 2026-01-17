import sys
import json
from pathlib import Path
from dataclasses import asdict

# -------------------------------------------------
# Path bootstrap
# -------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import json
from pathlib import Path
from layer4.run import run_layer4

# --- Write config ---
#'''
config = {
        "platform": "linux",
        "machine": {
            "arch": "x86_64",
            "cpu": "qemu64",
            "memory_mb": 512
        },
        "kernel": {
            "image": "C:/Users/Aadhav Nagarajan/OneDrive/Desktop/testing/vmlinuz-virt",
            "initramfs": "C:/Users/Aadhav Nagarajan/OneDrive/Desktop/testing/initramfs-obelisk.img",
            "cmdline": "console=tty0 panic=-1 obelisk.exec=/bin/busybox obelisk.args=echo,HELLO"
        },
        "console": "serial",
        "storage": {
            "boot_disk": "linux"
        }
        }

#'''
#'''
config = {
  "platform": "linux",
  "machine": {
    "arch": "x86_64",
    "cpu": "qemu64",
    "memory_mb": 512
  },
  "kernel": {
    "image": "C:/Users/Aadhav Nagarajan/OneDrive/Desktop/testing/vmlinuz-virt",
    "initramfs": "C:/Users/Aadhav Nagarajan/OneDrive/Desktop/testing/initramfs-obelisk.img",
    "cmdline": "console=tty0 panic=-1 obelisk.exec=/bin/busybox obelisk.args=sh,/artifact/test.sh"
  },
  "console": "serial",
  "storage": {
    "boot_disk": "linux"
  }
}
#'''
'''{
  "platform": "linux",
  "machine": {
    "arch": "x86_64",
    "memory_mb": 512
  },
  "kernel": {
    "image": "vmlinuz",
    "initramfs": "initramfs-obelisk.img",
    "cmdline": "console=ttyS0 panic=-1 obelisk.exec=/bin/busybox obelisk.args=sh,/artifact/test.sh"
  },
  "storage": {
    "boot_disk": "linux"
  }
}'''

cfg_path = Path("linux_test_config.json")
cfg_path.write_text(json.dumps(config, indent=2))

# --- Fake plan object (minimum fields used by L4) ---
class Plan:
    emulator = "qemu"
    variant = "linux-smoke"
    entry_point = ""
    config_path = str(cfg_path)
    artifact_root = ""
    fallback_timeout = 8000

plans = [Plan()]

profiles = run_layer4(plans)

for p in profiles:
    print(p)
