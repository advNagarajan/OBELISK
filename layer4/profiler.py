import time
from pathlib import Path

from layer4.models import ExecutionProfile
from layer4.phases import PHASES
from layer4.observers.config_semantics import parse_dosbox_config
from layer4.models import ExecutionProfile, ExecutionMode
from layer4.observers.telemetry import sample_cpu
from layer4.observers.console import analyze_console_output
from layer4.observers.process import observe_process

class ExecutionProfiler:
    def profile(self, plan, runner):
        if plan.emulator not in ("dosbox", "qemu", "zephyr"):
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
                execution_mode=ExecutionMode.PROCESS,
                phases=phases,
                sentinels={
                    "started": started,
                    "finished": finished,
                    "errorlevel": errorlevel,
                },
                config=config,
                sound_outcome=sound_outcome,
                host_telemetry=dict(host_telemetry)
            )
        
        # ============================================================
        # ZEPHYR (RTOS) PORTION
        # ============================================================
        elif plan.emulator == "zephyr":

            import json

            phases = {p: False for p in PHASES}

            with open(plan.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            timeout_sec = plan.fallback_timeout / 1000.0

            # Launch Zephyr
            proc = runner.launch(plan)
            phases["emulator_started"] = True

            if proc is None:
                print("[ExecutionProfiler] Interactive Zephyr mode — skipping profiling.")
                
                return ExecutionProfile(
                    emulator="zephyr",
                    variant=plan.variant,
                    entry_point=None,
                    execution_mode=ExecutionMode.SYSTEM,
                    phases=phases,
                    sentinels={
                        "interactive_mode": True
                    },
                    config=config,
                    sound_outcome=None,
                    host_telemetry={
                        "interactive": True
                    },
                )

            # RTOS has no filesystem concept — treat as mounted
            phases["filesystem_mounted"] = True

            time.sleep(timeout_sec)

            try:
                stdout, stderr = proc.communicate(timeout=2)
            except Exception:
                stdout, stderr = "", ""

            output = (stdout or "") + (stderr or "")
            lowered = output.lower()

            # -------------------------------------------------
            # STRICT Zephyr Boot Detection
            # -------------------------------------------------

            boot_banner = "*** booting zephyr os" in lowered
            board_name = config.get("board", "").lower()
            board_line_present = board_name in lowered
            wrapper_marker = "obelisk wrapper start" in lowered

            boot_detected = False

            # -------------------------------------------------
            # Zephyr boot confirmation logic
            # -------------------------------------------------

            if boot_banner:
                # Boot banner alone is strong evidence of system boot
                boot_detected = True

            # Wrapper marker is extra confirmation if present
            if wrapper_marker:
                boot_detected = True
            
            if not boot_banner:
                rtos_state = "no_boot"
            elif boot_banner and not board_line_present:
                rtos_state = "partial_boot"
            elif boot_detected:
                rtos_state = "boot_confirmed"
            else:
                rtos_state = "unknown"

            phases["entrypoint_invoked"] = boot_detected
            phases["control_transferred"] = boot_detected
            phases["stability_window_reached"] = boot_detected

            try:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=3)
            except Exception:
                pass

            return ExecutionProfile(
                emulator="zephyr",
                variant=plan.variant,
                entry_point=None,
                execution_mode=ExecutionMode.SYSTEM,
                phases=phases,
                sentinels={
                    "boot_banner_seen": boot_banner,
                    "board_line_seen": board_line_present,
                    "wrapper_marker_seen": wrapper_marker,
                    "rtos_boot_detected": boot_detected,
                },
                config=config,
                sound_outcome=None,
                host_telemetry={
                    "stdout_sample": stdout[:500]
                },
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
            
            timeout_ms = execution.get("timeout_ms", plan.fallback_timeout)

            timeout_sec = timeout_ms / 1000.0

            # --- Launch QEMU ---
            proc = runner.launch(plan)
            phases["emulator_started"] = True

            if not plan.variant.startswith("linux"):
                time.sleep(2)
                phases["filesystem_mounted"] = True

            # ============================================================
            # LINUX IS NON-TERMINATING — DO NOT TOUCH PROCESS
            # ============================================================
            if plan.variant.startswith("linux"):

                time.sleep(timeout_sec)

                serial_log = Path("serial.log")

                boot_seen = False
                artifact_started = False
                artifact_exited = False

                if serial_log.exists():
                    text = serial_log.read_text(errors="ignore").lower()

                    boot_seen = "obelisk: custom init starting" in text
                    artifact_started = "obelisk: exec" in text
                    artifact_exited = "artifact exited with code" in text

                phases["filesystem_mounted"] = boot_seen
                phases["entrypoint_invoked"] = artifact_started
                phases["control_transferred"] = artifact_started
                phases["stability_window_reached"] = boot_seen

                return ExecutionProfile(
                    emulator="qemu",
                    variant=plan.variant,
                    entry_point=None,
                    execution_mode=ExecutionMode.SYSTEM,
                    phases=phases,
                    sentinels={
                        "boot_seen": boot_seen,
                        "artifact_started": artifact_started,
                        "artifact_exited": artifact_exited,
                    },
                    config=config,
                    sound_outcome=None,
                    host_telemetry={
                        "linux_serial_observed": serial_log.exists()
                    },
                )
            time.sleep(timeout_sec)
            try:
                stdout, stderr = proc.communicate(timeout=2)
            except Exception:
                stdout, stderr = "", ""

            # --- IMPORTANT FIX ---
            # QEMU sentinels live in FAT-backed run_dir, NOT artifact_root
            run_dir = getattr(proc, "_obelisk_run_dir", None)
            if run_dir is None:
                output = stdout + stderr
                started = (
                    "Linux version" in output or
                    "Kernel command line" in output
                )
                finished = proc.poll() is not None
                errorlevel = proc.returncode
            else:
                # DOS QEMU path: use FAT-backed sentinels
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
            phases["stability_window_reached"] = started and not finished
            try:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=3)
            except Exception:
                pass

            # --- Capture console output ---
            

            console_facts = analyze_console_output(stdout, stderr)
            process_facts = observe_process(proc, timeout=1)

            return ExecutionProfile(
                emulator="qemu",
                variant=plan.variant,
                entry_point=plan.entry_point,
                execution_mode=ExecutionMode.PROCESS,
                phases=phases,
                sentinels={
                    "started": started,
                    "finished": finished,
                    "errorlevel": errorlevel,
                },
                config=config,
                sound_outcome="enabled",
                host_telemetry={
                    **console_facts,
                    **process_facts,
                },
            )

