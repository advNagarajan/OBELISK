import json
import os
from typing import List

from layer3.adapters.base import EmulatorAdapter
from layer3.launchplan import LaunchPlan
from layer3.linux_intent import LinuxExecutionIntent


class LinuxQEMUAdapter(EmulatorAdapter):

    def supports(self, system_profile) -> bool:
        return system_profile.execution_surface == "linux_contract"

    def generate_variants(
        self,
        intent: LinuxExecutionIntent,
        system_profile
    ) -> List[LaunchPlan]:

        output_dir = "layer3_output"
        os.makedirs(output_dir, exist_ok=True)

        config_path = os.path.join(output_dir, "qemu_linux.json")

        # -------------------------------------------------
        # Determine artifact entrypoint
        # -------------------------------------------------
        if intent.exec_args:
            entrypoint = intent.exec_args[-1].split("/")[-1]
        else:
            entrypoint = intent.exec_path.split("/")[-1]

        # -------------------------------------------------
        # Construct Linux execution config
        # -------------------------------------------------
        config = {
            "platform": "linux",

            "machine": {
                "arch": "x86_64",
                "memory_mb": intent.memory_mb
            },

            "kernel": {
                "image": intent.kernel_path,
                "cmdline": "console=ttyS0 panic=-1"
            },

            "artifact": {
                "path": system_profile.artifact_root,
                "entrypoint": entrypoint
            }
        }

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        return [
            LaunchPlan(
                emulator="qemu",
                config_path=config_path,
                artifact_root=system_profile.artifact_root,
                entry_point=None,
                fallback_timeout=intent.timeout_ms,
                confidence=0.9,
                variant="linux",
                priority=1
            )
        ]