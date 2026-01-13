from typing import List
from layer3.adapters.base import EmulatorAdapter
from layer3.launchplan import LaunchPlan
from layer3.canonical import CanonicalMachine


class DOSBoxAdapter(EmulatorAdapter):

    def supports(self, system_profile) -> bool:
        # DOSBox only supports program-style execution
        return system_profile.execution_surface == "program"

    def generate_variants(
        self,
        machine: CanonicalMachine,
        system_profile
    ) -> List[LaunchPlan]:

        artifact_root = system_profile.artifact_root

        entry_point = max(
            system_profile.entry_points,
            key=lambda e: e.confidence
        ).path

        plans = []

        # Variant 1: minimal viable (strict)
        plans.append(
            self._make_plan(
                machine, entry_point, artifact_root,
                variant="minimal",
                priority=1,
                cycles="3000",
                sound=False,
                svga=False
            )
        )

        # Variant 2: minimal + sound
        if machine.sound:
            plans.append(
                self._make_plan(
                    machine, entry_point, artifact_root,
                    variant="minimal+sound",
                    priority=2,
                    cycles="3000",
                    sound=True,
                    svga=False
                )
            )

        # Variant S: sound probe (exploratory)
        sound = system_profile.sound

        sound_probe = (
            sound is not None and
            sound.requirement == "optional" and
            sound.confidence < 0.5 and
            len(sound.supported_devices) == 0
        )

        if sound_probe:
            plans.append(
                self._make_plan(
                    machine,
                    entry_point,
                    artifact_root,
                    variant="sound-probe",
                    priority=2,
                    cycles="3000",
                    sound=True,
                    svga=False
                )
            )

        # Variant 3: auto CPU (less strict timing)
        plans.append(
            self._make_plan(
                machine, entry_point, artifact_root,
                variant="auto-cpu",
                priority=3,
                cycles="auto",
                sound=False,
                svga=False
            )
        )

        # Variant 4: permissive fallback
        plans.append(
            self._make_plan(
                machine, entry_point, artifact_root,
                variant="permissive",
                priority=4,
                cycles="auto",
                sound=True,
                svga=True
            )
        )

        return plans

    def _make_plan(
        self,
        machine: CanonicalMachine,
        entry_point: str,
        artifact_root: str,
        variant: str,
        priority: int,
        cycles: str,
        sound: bool,
        svga: bool
    ) -> LaunchPlan:

        conf_path = f"dosbox_{variant}.conf"

        with open(conf_path, "w") as f:
            # ---------------- CPU ----------------
            f.write("[cpu]\n")
            f.write(f"cputype={machine.cpu}\n")
            f.write("core=normal\n")
            f.write(f"cycles={cycles}\n\n")

            # ---------------- Memory ----------------
            f.write("[memory]\n")
            f.write(f"memsize={machine.memory_mb}\n\n")

            # ---------------- Video ----------------
            f.write("[dosbox]\n")
            f.write("machine=svga_s3\n" if svga else "machine=vga\n")
            f.write("\n")

            # ---------------- Sound ----------------
            f.write("[sblaster]\n")
            if sound:
                f.write("sbtype=sb16\n")
            else:
                f.write("sbtype=none\n")

            # ---------------- AUTOEXEC ----------------
            f.write("\n[autoexec]\n")
            f.write("@echo off\n")
            f.write(f'mount c "{artifact_root}"\n')
            f.write("c:\n")

            # Execution sentinels (Layer-4 friendly)
            f.write("echo START > C:\\STARTED.TXT\n")
            f.write(f"{entry_point}\n")
            f.write("echo %errorlevel% > C:\\ERRLVL.TXT\n")
            f.write("echo END > C:\\FINISH.TXT\n")

        return LaunchPlan(
            emulator="dosbox",
            config_path=conf_path,
            artifact_root=artifact_root,
            entry_point=entry_point,
            timeout=20,
            confidence=0.6,
            variant=variant,
            priority=priority
        )
