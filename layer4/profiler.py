import time
from pathlib import Path

from layer4.models import ExecutionProfile
from layer4.phases import PHASES
from layer4.observers.config_semantics import parse_dosbox_config
from layer4.observers.telemetry import sample_cpu


class ExecutionProfiler:
    def profile(self, plan, runner):
        if plan.emulator not in ("dosbox", "qemu"):
            raise NotImplementedError(
                f"Layer 4 Phase 2 supports only DOSBox and QEMU got: {plan.emulator}"
            )

        # ============================================================
        # DOSBOX PORTION — UNCHANGED
        # ============================================================
        if plan.emulator == "dosbox":
            phases = {p: False for p in PHASES}

            artifact_root = Path(plan.artifact_root)

            for fname in ["STARTED.TXT", "ERRLVL.TXT", "FINISH.TXT"]:
                f = artifact_root / fname
                if f.exists():
                    f.unlink()

            proc, _ = runner.launch(plan)
            phases["emulator_started"] = True

            time.sleep(1)
            phases["filesystem_mounted"] = True

            OBSERVATION_WINDOW = 8
            time.sleep(OBSERVATION_WINDOW)

            started = (artifact_root / "STARTED.TXT").exists()
            finished = (artifact_root / "FINISH.TXT").exists()

            errorlevel = None
            err_file = artifact_root / "ERRLVL.TXT"
            if err_file.exists():
                try:
                    errorlevel = int(err_file.read_text().strip())
                except ValueError:
                    errorlevel = None

            phases["entrypoint_invoked"] = started
            phases["control_transferred"] = started
            phases["stability_window_reached"] = (
                started and (
                    not finished or
                    (finished and errorlevel == 0)
                )
            )

            host_telemetry = sample_cpu(proc)

            try:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except Exception:
                        proc.kill()
            except Exception:
                pass

            config = parse_dosbox_config(plan.config_path)

            sound_outcome = None
            sound_enabled = config.get("sound_enabled", False)

            if not sound_enabled:
                if started and not finished:
                    sound_outcome = "init_block"
                elif started and finished:
                    sound_outcome = "tolerated"

            return ExecutionProfile(
                emulator="dosbox",
                variant=plan.variant,
                entry_point=plan.entry_point,
                phases=phases,
                sentinels={
                    "started": started,
                    "finished": finished,
                    "errorlevel": errorlevel,
                },
                config=config,
                sound_outcome=sound_outcome,
                host_telemetry=host_telemetry,
            )

        # ============================================================
        # QEMU PORTION — FIXED
        # ============================================================
        elif plan.emulator == "qemu":
            import json

            phases = {p: False for p in PHASES}

            with open(plan.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            execution = config.get("execution", {})
            timeout_ms = execution.get("timeout_ms")
            if timeout_ms is None:
                raise ValueError("QEMU execution requires timeout_ms in config")

            timeout_sec = timeout_ms / 1000.0

            # --- Launch QEMU ---
            proc = runner.launch(plan)
            phases["emulator_started"] = True

            time.sleep(2)
            phases["filesystem_mounted"] = True

            time.sleep(timeout_sec)

            # --- IMPORTANT FIX ---
            # QEMU sentinels live in FAT-backed run_dir, NOT artifact_root
            run_dir = getattr(proc, "_obelisk_run_dir", None)
            if run_dir is None:
                raise RuntimeError("QEMU runner did not expose _obelisk_run_dir")

            started = (run_dir / "STARTED.TXT").exists()
            finished = (run_dir / "FINISH.TXT").exists()

            errorlevel = None
            err_file = run_dir / "ERRLVL.TXT"
            if err_file.exists():
                try:
                    errorlevel = int(err_file.read_text().strip())
                except ValueError:
                    errorlevel = None

            # --- FIXED PHASE LOGIC ---
            # Long-running programs (DOOM) are valid
            phases["entrypoint_invoked"] = started
            phases["control_transferred"] = started
            phases["stability_window_reached"] = (
                started and (
                    not finished or
                    (finished and errorlevel == 0)
                )
            )
            try:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=3)
            except Exception:
                pass

            return ExecutionProfile(
                emulator="qemu",
                variant=plan.variant,
                entry_point=plan.entry_point,
                phases=phases,
                sentinels={
                    "started": started,
                    "finished": finished,
                    "errorlevel": errorlevel,
                },
                config={},  # QEMU semantics parsed later if needed
                sound_outcome=None,
                host_telemetry={},
            )
