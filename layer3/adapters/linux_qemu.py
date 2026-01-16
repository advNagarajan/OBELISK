import json
import os
from typing import List

from layer3.adapters.base import EmulatorAdapter
from layer3.launchplan import LaunchPlan
from layer3.linux_intent import LinuxExecutionIntent

class LinuxQEMUAdapter(EmulatorAdapter):

    def supports(self, system_profile) -> bool:
        return system_profile.execution_surface.startswith("linux")

    def generate_variants(
        self,
        intent: LinuxExecutionIntent,
        system_profile
    ) -> List[LaunchPlan]:

        output_dir = "layer3_output"
        os.makedirs(output_dir, exist_ok=True)

        config_path = os.path.join(output_dir, "qemu_linux.json")

        config = {
            "kernel": intent.kernel_path,
            "initramfs": intent.initramfs_path,
            "append": "console=ttyS0 panic=-1",

            "memory_mb": intent.memory_mb,
            "graphics": intent.graphics,
            "console": intent.console,

            "execution": {
                "mode": intent.mode,
                "entry_point": intent.entry_point,
                "timeout_ms": intent.timeout_ms
            }
        }

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        return [
            LaunchPlan(
                emulator="qemu",
                config_path=config_path,
                artifact_root=system_profile.artifact_root,
                entry_point=intent.entry_point,
                fallback_timeout=intent.timeout_ms,
                confidence=0.9,
                variant="linux",
                priority=1
            )
        ]
