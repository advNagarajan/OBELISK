"""
OBELISK – Phase 2.5 Linux QEMU Execution Test

Purpose:
- Validate Linux execution path (Layer 4 only)
- No Layer 1 ingestion
- No Layer 2 inference
- Layer 3 intent is explicit and frozen

This tests:
- QEMU kernel boot
- initramfs execution
- stdout/stderr capture
- timeout handling
"""

import sys
import json
from pathlib import Path
from dataclasses import asdict

# -------------------------------------------------
# Path bootstrap
# -------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# -------------------------------------------------
# Imports
# -------------------------------------------------
from layer3.launchplan import LaunchPlan
from layer4.run import run_layer4


# -------------------------------------------------
# Config paths (MUST EXIST)
# -------------------------------------------------
LINUX_KERNEL = Path("runtime/linux/base/vmlinuz")
LINUX_INITRAMFS = Path("runtime/linux/base/initramfs.cpio")

assert LINUX_KERNEL.exists(), "Missing Linux kernel"
assert LINUX_INITRAMFS.exists(), "Missing initramfs.cpio"


# -------------------------------------------------
# Layer-3 config file (authoritative intent)
# -------------------------------------------------
L3_CONFIG_PATH = Path("layer3_output/linux_runtime.json")
L3_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

if not L3_CONFIG_PATH.exists():
    L3_CONFIG_PATH.write_text(
        json.dumps(
            {
                "storage": {
                    "boot_disk": "linux"
                },
                "execution": {
                    "timeout_ms": 5000
                },
                "graphics": {
                    "framebuffer": True
                },
                "sound": ["alsa"]
            },
            indent=2
        ),
        encoding="utf-8"
    )


# -------------------------------------------------
# Test: Linux QEMU execution
# -------------------------------------------------
def test_linux_qemu_execution():
    print("\n" + "=" * 90)
    print("TEST – LINUX QEMU EXECUTION (PHASE 2.5)")
    print("=" * 90 + "\n")

    # -----------------------------
    # Construct Layer-3 LaunchPlan
    # -----------------------------
    plan = LaunchPlan(
        emulator="qemu",
        config_path="layer3_output/qemu_linux.json",
        artifact_root="",
        entry_point="/init",
        fallback_timeout=30000,
        confidence=1.0,
        variant="linux",
        priority=0,
    )

    print("LaunchPlan:")
    print(asdict(plan))

    # -----------------------------
    # Execute via Layer 4
    # -----------------------------
    profiles = run_layer4([plan])
    profile = profiles[0]

    print("\nExecution Profile:")
    print(profile)

    # -----------------------------
    # Assertions (Phase 2.5 invariants)
    # -----------------------------
    phases = profile.phases

    assert phases.get("emulator_started"), "QEMU did not start"
    assert phases.get("entrypoint_invoked"), "Linux init not invoked"
    assert phases.get("control_transferred"), "Control not transferred"
    assert phases.get("stability_window_reached"), "Stability window not reached"

    print("\n✅ Linux QEMU execution PASSED")


# -------------------------------------------------
# Main
# -------------------------------------------------
if __name__ == "__main__":
    test_linux_qemu_execution()
