import json
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

        if system_profile.execution_surface == "program":
            plans.extend(
                self._program_variants(machine, system_profile)
            )

        if system_profile.execution_surface == "boot_disk":
            plans.extend(
                self._boot_variants(machine, system_profile)
            )

        return plans

    # =================================================
    # Program execution (FreeDOS-style)
    # =================================================
    def _program_variants(
        self,
        machine: CanonicalMachine,
        system_profile
    ) -> List[LaunchPlan]:

        artifact_root = system_profile.artifact_root
        entry = max(
            system_profile.entry_points,
            key=lambda e: e.confidence
        ).path

        plans = []

        plans.append(
            self._make_plan(
                machine,
                artifact_root,
                entry_point=entry,
                variant="freedos-minimal",
                priority=3,
                permissive=False
            )
        )

        plans.append(
            self._make_plan(
                machine,
                artifact_root,
                entry_point=entry,
                variant="freedos-permissive",
                priority=4,
                permissive=True
            )
        )

        return plans

    # =================================================
    # Bootable disk execution
    # =================================================
    def _boot_variants(
        self,
        machine: CanonicalMachine,
        system_profile
    ) -> List[LaunchPlan]:

        artifact_root = system_profile.artifact_root

        plans = []

        plans.append(
            self._make_plan(
                machine,
                artifact_root,
                entry_point="",
                variant="boot-conservative",
                priority=2,
                permissive=False
            )
        )

        plans.append(
            self._make_plan(
                machine,
                artifact_root,
                entry_point="",
                variant="boot-permissive",
                priority=3,
                permissive=True
            )
        )

        return plans

    # =================================================
    # Config writer (Layer-3 responsibility)
    # =================================================
    def _make_plan(
        self,
        machine: CanonicalMachine,
        artifact_root: str,
        entry_point: str,
        variant: str,
        priority: int,
        permissive: bool
    ) -> LaunchPlan:

        config_path = f"qemu_{variant}.json"

        config = {
            "machine": {
                "arch": "i386",
                "cpu": machine.cpu if not permissive else "max",
                "memory_mb": machine.memory_mb if not permissive else max(machine.memory_mb, 64)
            },
            "graphics": machine.graphics,
            "sound": machine.sound,
            "dos_extender": machine.dos_extender,
            "execution": {
                "mode": (
                    "program" if entry_point else "boot_disk"
                ),
                "entry_point": entry_point
            }
        }

        with open(config_path, "w") as f:
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
