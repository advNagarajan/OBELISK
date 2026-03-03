import subprocess
import shutil
import json
import os
import hashlib
from pathlib import Path

from config import ZEPHYR_BASE_PATH


class ZephyrRunner:

    BUILD_DIR_NAME = ".obelisk_zephyr_build"
    TEMP_ROOT = Path("D:/obelisk_tmp")

    # -------------------------------------------------
    # MANUAL TOGGLE
    # False = deterministic capture (default)
    # True  = interactive QEMU window
    # -------------------------------------------------
    INTERACTIVE_CONSOLE = False

    def launch(self, plan):

        # -------------------------------------------------
        # Load Layer 3 config
        # -------------------------------------------------
        with open(plan.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        board = config["board"]
        original_source = Path(config["source_root"]).resolve()

        if not original_source.exists():
            raise FileNotFoundError(
                f"Zephyr source_root not found: {original_source}"
            )

        zephyr_base = Path(ZEPHYR_BASE_PATH).resolve()
        if not zephyr_base.exists():
            raise FileNotFoundError(
                f"ZEPHYR_BASE_PATH does not exist: {zephyr_base}"
            )

        # -------------------------------------------------
        # Kill stray QEMU (Windows safety)
        # -------------------------------------------------
        subprocess.run(
            ["taskkill", "/F", "/IM", "qemu-system-i386.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # -------------------------------------------------
        # Create deterministic temp sandbox (no spaces)
        # -------------------------------------------------
        self.TEMP_ROOT.mkdir(parents=True, exist_ok=True)

        artifact_hash = hashlib.sha256(
            str(original_source).encode()
        ).hexdigest()[:16]

        temp_source = (self.TEMP_ROOT / artifact_hash).resolve()

        if temp_source.exists():
            shutil.rmtree(temp_source)

        shutil.copytree(original_source, temp_source)

        build_dir = (temp_source / self.BUILD_DIR_NAME).resolve()

        if build_dir.exists():
            shutil.rmtree(build_dir)

        # -------------------------------------------------
        # Prepare environment
        # -------------------------------------------------
        env = os.environ.copy()
        env["ZEPHYR_BASE"] = zephyr_base.as_posix()

        # -------------------------------------------------
        # Configure (CMake)
        # -------------------------------------------------
        cmake_cmd = [
            "cmake",
            "-B", str(build_dir),
            "-S", str(temp_source),
            "-GNinja",
            f"-DBOARD={board}",
        ]

        print("\n[ZephyrRunner] CMake configure...")
        subprocess.run(cmake_cmd, check=True, env=env)

        # -------------------------------------------------
        # Build (Ninja)
        # -------------------------------------------------
        ninja_cmd = [
            "ninja",
            "-C", str(build_dir)
        ]

        print("[ZephyrRunner] Ninja build...")
        subprocess.run(ninja_cmd, check=True, env=env)

        # -------------------------------------------------
        # Locate built ELF
        # -------------------------------------------------
        zephyr_elf = build_dir / "zephyr" / "zephyr.elf"

        if not zephyr_elf.exists():
            raise FileNotFoundError(
                f"Zephyr ELF not found: {zephyr_elf}"
            )

        # -------------------------------------------------
        # QEMU executable
        # -------------------------------------------------
        qemu_exe = r"C:\Program Files\qemu\qemu-system-i386.exe"

        if not Path(qemu_exe).exists():
            raise FileNotFoundError(
                f"QEMU executable not found: {qemu_exe}"
            )

        # -------------------------------------------------
        # Exact Zephyr QEMU invocation
        # (matches `ninja run -v`)
        # -------------------------------------------------
        qemu_cmd = [
            qemu_exe,
            "-m", "32",
            "-cpu", "qemu32,+nx,+pae",
            "-machine", "q35",
            "-device", "isa-debug-exit,iobase=0xf4,iosize=0x04",
            "-no-reboot",
            "-nographic",
            "-machine", "accel=tcg",
            "-net", "none",
            "-chardev", "stdio,id=con,mux=on",
            "-serial", "chardev:con",
            "-mon", "chardev=con,mode=readline",
            "-icount", "shift=5,align=off,sleep=off",
            "-rtc", "clock=vm",
            "-kernel", str(zephyr_elf),
        ]

        # -------------------------------------------------
        # INTERACTIVE MODE
        # -------------------------------------------------
        if self.INTERACTIVE_CONSOLE:

            print("[ZephyrRunner] Launching interactive QEMU console...")

            subprocess.Popen(
                qemu_cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                env=env
            )

            # In interactive mode, profiler must skip
            return None

        # -------------------------------------------------
        # DETERMINISTIC MODE (capture output)
        # -------------------------------------------------
                # -------------------------------------------------
        # DETERMINISTIC MODE (capture via serial file)
        # -------------------------------------------------

        print("[ZephyrRunner] Launching QEMU (deterministic mode)...")

        serial_log = build_dir / "serial.log"

        qemu_cmd = [
            qemu_exe,
            "-m", "32",
            "-cpu", "qemu32,+nx,+pae",
            "-machine", "q35",
            "-device", "isa-debug-exit,iobase=0xf4,iosize=0x04",
            "-no-reboot",
            "-nographic",
            "-machine", "accel=tcg",
            "-net", "none",
            "-serial", f"file:{serial_log}",
            "-kernel", str(zephyr_elf),
        ]

        proc = subprocess.Popen(
            qemu_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env
        )

        # -------------------------------------------------
        # Profiling window (RTOS stability window)
        # -------------------------------------------------
        import time
        time.sleep(3)   # allow Zephyr to boot + print

        # Kill QEMU
        proc.terminate()

        # -------------------------------------------------
        # Read serial output
        # -------------------------------------------------
        import re

        if serial_log.exists():
            with open(serial_log, "r", errors="ignore") as f:
                serial_output = f.read()
                ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
                serial_output = ansi_escape.sub('', serial_output)
        else:
            serial_output = ""

        # Dummy object for profiler compatibility
        class DummyProc:
            def communicate(self, timeout=None):
                return serial_output, ""
            def poll(self):
                return 0
            def terminate(self):
                pass

        dummy = DummyProc()
        dummy._obelisk_execution_model = "rtos"
        dummy._obelisk_platform = "zephyr"

        return dummy