import time
from pathlib import Path

from layer4.models import ExecutionProfile
from layer4.phases import PHASES
from layer4.observers.config_semantics import parse_dosbox_config
from layer4.utils.pcem_config import write_minimal_pcem_config
from layer4.observers.telemetry import sample_cpu


class ExecutionProfiler:
    def profile(self, plan, runner):

        if plan.emulator == "pcem":
            # ---- Phase initialization ----
            phases = {p: False for p in PHASES}

            # ---- Write minimal PCem config ----
            write_minimal_pcem_config(
                plan.config_path,
                plan.artifact_root
            )

            # ---- Launch PCem ----
            proc = runner.launch(plan.config_path)
            phases["emulator_started"] = True

            # ---- Observation window (liveness only) ----
            start = time.time()
            alive = True

            while time.time() - start < plan.timeout:
                if proc.poll() is not None:
                    alive = False
                    break
                time.sleep(1)

            phases["stability_window_reached"] = alive

            # ---- Optional diagnostics ----
            host_telemetry = sample_cpu(proc)

            # ---- Cleanup ----
            try:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except Exception:
                        proc.kill()
            except Exception:
                pass

            # ---- Build minimal execution profile ----
            return ExecutionProfile(
                emulator="pcem",
                variant=plan.variant,
                entry_point="",              # no entry point for OS boot
                phases=phases,
                sentinels={},                # none in Phase 1
                config={"pcem_config": plan.config_path},
                sound_outcome=None,
                host_telemetry=host_telemetry
            )
        
        elif plan.emulator == 'dosbox':
            # ---- Phase initialization ----
            phases = {p: False for p in PHASES}

            # ---- Resolve artifact root (mounted as C:) ----
            artifact_root = Path(plan.artifact_root)

            # ---- CLEANUP (MUST BE BEFORE LAUNCH) ----
            for fname in ["STARTED.TXT", "ERRLVL.TXT", "FINISH.TXT"]:
                f = artifact_root / fname
                if f.exists():
                    f.unlink()

            # ---- Launch emulator ----
            proc, _ = runner.launch(plan)
            phases["emulator_started"] = True

            # ---- Allow AUTOEXEC to begin ----
            time.sleep(1)
            phases["filesystem_mounted"] = True

            # ---- Observation window ----
            OBSERVATION_WINDOW = 8
            time.sleep(OBSERVATION_WINDOW)

            # ---- Sentinel files (ground truth) ----
            started = (artifact_root / "STARTED.TXT").exists()
            finished = (artifact_root / "FINISH.TXT").exists()

            errorlevel = None
            err_file = artifact_root / "ERRLVL.TXT"
            if err_file.exists():
                try:
                    errorlevel = int(err_file.read_text().strip())
                except ValueError:
                    errorlevel = None  # valid DOS behavior

            # ---- Phase logic (NO inference) ----
            phases["entrypoint_invoked"] = started
            phases["control_transferred"] = started

            phases["stability_window_reached"] = (
                started and (
                    not finished or
                    (finished and errorlevel == 0)
                )
            )

            # ---- Optional diagnostics ----
            host_telemetry = sample_cpu(proc)

            # ---- Cleanup emulator ----
            try:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except Exception:
                        proc.kill()
            except Exception:
                pass

            # ---- Config metadata (input, not execution) ----
            config = parse_dosbox_config(plan.config_path)

            sound_outcome = None

            sound_enabled = config.get("sound_enabled", False)

            if not sound_enabled:
                if started and not finished:
                    # Entrypoint reached, but program never completed
                    sound_outcome = "init_block"

                elif started and finished:
                    # Program ran fine without sound
                    sound_outcome = "tolerated"

            # ---- Build final profile ----
            return ExecutionProfile(
                emulator="dosbox",
                variant=plan.variant,
                entry_point=plan.entry_point,
                phases=phases,
                sentinels={
                    "started": started,
                    "finished": finished,
                    "errorlevel": errorlevel
                },
                config=config,
                sound_outcome=sound_outcome,
                host_telemetry=host_telemetry
            )
