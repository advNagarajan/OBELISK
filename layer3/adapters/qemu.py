import json
import os
from typing import List

from layer3.adapters.base import EmulatorAdapter
from layer3.launchplan import LaunchPlan
from layer3.canonical import CanonicalMachine


class QEMUAdapter(EmulatorAdapter):

    def supports(self, system_profile) -> bool:
        return system_profile.execution_surface in ("program", "boot_disk")

    def generate_variants(
        self,
        machine: CanonicalMachine,
        system_profile
    ) -> List[LaunchPlan]:

        plans = []
        artifact_root = system_profile.artifact_root

        if system_profile.execution_surface == "program":
            plans.extend(
                self._program_variants(machine, artifact_root, system_profile)
            )

        if system_profile.execution_surface == "boot_disk":
            plans.extend(
                self._boot_variants(machine, artifact_root)
            )

        return plans

    # -------------------------------------------------
    # Program-style execution
    # -------------------------------------------------
    def _program_variants(
        self,
        machine: CanonicalMachine,
        artifact_root: str,
        system_profile
    ) -> List[LaunchPlan]:

        entry = max(
            system_profile.entry_points,
            key=lambda e: e.confidence
        ).path

        return [
            self._make_plan(
                machine=machine,
                artifact_root=artifact_root,
                entry_point=entry,
                variant="program-minimal",
                priority=3,
                permissive=False
            ),
            self._make_plan(
                machine=machine,
                artifact_root=artifact_root,
                entry_point=entry,
                variant="program-permissive",
                priority=4,
                permissive=True
            )
        ]

    # -------------------------------------------------
    # Bootable disk execution
    # -------------------------------------------------
    def _boot_variants(
        self,
        machine: CanonicalMachine,
        artifact_root: str
    ) -> List[LaunchPlan]:

        return [
            self._make_plan(
                machine=machine,
                artifact_root=artifact_root,
                entry_point="",
                variant="boot-minimal",
                priority=2,
                permissive=False
            ),
            self._make_plan(
                machine=machine,
                artifact_root=artifact_root,
                entry_point="",
                variant="boot-permissive",
                priority=3,
                permissive=True
            )
        ]

    # -------------------------------------------------
    # JSON config writer (Layer 3 responsibility)
    # -------------------------------------------------
    def _make_plan(
        self,
        machine: CanonicalMachine,
        artifact_root: str,
        entry_point: str,
        variant: str,
        priority: int,
        permissive: bool
    ) -> LaunchPlan:

        output_dir = "layer3_output"
        os.makedirs(output_dir, exist_ok=True)

        config_filename = f"qemu_{variant}.json"
        config_path = os.path.join(output_dir, config_filename)

        config = {
            "machine": {
                "arch": "i386",
                "cpu": machine.cpu if not permissive else "max",
                "memory_mb": (
                    machine.memory_mb
                    if not permissive
                    else max(machine.memory_mb, 64)
                )
            },
            "graphics": machine.graphics,
            "sound": machine.sound,
            "dos_extender": machine.dos_extender,

            # NEW — declarative storage intent
            "storage": {
                "boot_disk": "dos",
                "writable_fs": True,
                "fs_type": "fat"
            },

            "execution": {
                "mode": "program" if entry_point else "boot_disk",
                "entry_point": entry_point,

                # NEW — execution semantics
                "working_directory": "C:\\",
                "autoexec": True
            }
        }

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        return LaunchPlan(
            emulator="qemu",
            config_path=config_path,
            artifact_root=artifact_root,
            entry_point=entry_point,
            timeout=120 if entry_point == "" else 30,
            confidence=0.6 if not permissive else 0.5,
            variant=variant,
            priority=priority
        )
