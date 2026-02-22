import json
import os
from typing import List

from layer3.adapters.base import EmulatorAdapter
from layer3.launchplan import LaunchPlan
from layer3.rtos_intent import RTOSExecutionIntent


class ZephyrAdapter(EmulatorAdapter):

    def supports(self, system_profile) -> bool:
        return system_profile.execution_surface in (
            "rtos_project",
            "rtos_wrapped"
        )

    def generate_variants(
        self,
        intent: RTOSExecutionIntent,
        system_profile
    ) -> List[LaunchPlan]:

        output_dir = "layer3_output"
        os.makedirs(output_dir, exist_ok=True)

        plans = []

        # ---------------------------------------
        # Pull inference evidence (if present)
        # ---------------------------------------
        evidence = system_profile.execution_evidence.get(
            "rtos_resolution", {}
        )

        inferred_confidence = evidence.get("confidence", 0.6)

        # ---------------------------------------
        # Variant 1 — Inferred Board
        # ---------------------------------------
        inferred_config_path = os.path.join(
            output_dir, "zephyr_inferred.json"
        )

        inferred_config = {
            "platform": "zephyr",
            "board": intent.board,
            "source_root": intent.source_root,
            "wrapper_generated": intent.wrapper_generated
        }

        with open(inferred_config_path, "w") as f:
            json.dump(inferred_config, f, indent=2)

        plans.append(
            LaunchPlan(
                emulator="zephyr",
                config_path=inferred_config_path,
                artifact_root=system_profile.artifact_root,
                entry_point=None,
                fallback_timeout=intent.timeout_ms,
                confidence=inferred_confidence,
                variant="zephyr-inferred",
                priority=1
            )
        )

        # ---------------------------------------
        # Variant 2 — Deterministic Fallback
        # ---------------------------------------
        if intent.board != "qemu_x86":

            fallback_config_path = os.path.join(
                output_dir, "zephyr_fallback.json"
            )

            fallback_config = {
                "platform": "zephyr",
                "board": "qemu_x86",
                "source_root": intent.source_root,
                "wrapper_generated": intent.wrapper_generated
            }

            with open(fallback_config_path, "w") as f:
                json.dump(fallback_config, f, indent=2)

            plans.append(
                LaunchPlan(
                    emulator="zephyr",
                    config_path=fallback_config_path,
                    artifact_root=system_profile.artifact_root,
                    entry_point=None,
                    fallback_timeout=intent.timeout_ms,
                    confidence=0.6,
                    variant="zephyr-fallback",
                    priority=2
                )
            )

        return plans