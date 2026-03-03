import subprocess
import shutil
import json
import os
from pathlib import Path
import hashlib

from config import ZEPHYR_BASE_PATH


class ZephyrRunner:

    BUILD_DIR_NAME = ".obelisk_zephyr_build"
    TEMP_ROOT = Path("D:/obelisk_tmp")

    # -----------------------------
    # MANUAL TOGGLE (DEFAULT ON)
    # -----------------------------
    INTERACTIVE_CONSOLE = False

    def launch(self, plan):

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

        zephyr_base_cmake = zephyr_base.as_posix()

        # -------------------------------------------------
        # Create temp safe build root (no spaces, D drive)
        # -------------------------------------------------
        self.TEMP_ROOT.mkdir(parents=True, exist_ok=True)

        artifact_hash = hashlib.sha256(
            str(original_source).encode()
        ).hexdigest()[:16]

        temp_source = (self.TEMP_ROOT / artifact_hash).resolve()

        # Clean previous temp copy
        import subprocess

        subprocess.run(
            ["taskkill", "/F", "/IM", "qemu-system-i386.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        if temp_source.exists():
            try:
                shutil.rmtree(temp_source)
            except PermissionError:
                print("[ZephyrRunner] Temp directory locked (likely interactive QEMU still running).")
                print("Close the QEMU window before rerunning.")
                raise

        shutil.copytree(original_source, temp_source)

        # -------------------------------------------------
        # Dedicated OBELISK build directory
        # -------------------------------------------------
        build_dir = (temp_source / self.BUILD_DIR_NAME).resolve()

        if build_dir.exists():
            shutil.rmtree(build_dir)

        # -------------------------------------------------
        # Environment
        # -------------------------------------------------
        env = os.environ.copy()
        env["ZEPHYR_BASE"] = zephyr_base_cmake

        # -------------------------------------------------
        # Configure
        # -------------------------------------------------
        cmake_cmd = [
            "cmake",
            "-B", str(build_dir),
            "-S", str(temp_source),
            "-GNinja",
            f"-DBOARD={board}",
            f"-DZEPHYR_BASE={zephyr_base_cmake}"
        ]

        print("\n[ZephyrRunner] CMake configure...")
        subprocess.run(
            cmake_cmd,
            check=True,
            env=env
        )

        # -------------------------------------------------
        # Build
        # -------------------------------------------------
        ninja_cmd = [
            "ninja",
            "-C", str(build_dir)
        ]

        print("[ZephyrRunner] Ninja build...")
        subprocess.run(
            ninja_cmd,
            check=True,
            env=env
        )

        # -------------------------------------------------
        # Locate executable
        # -------------------------------------------------
        # -------------------------------------------------
        # Run using Zephyr's official run target
        # -------------------------------------------------
        run_cmd = [
            "cmake",
            "--build", str(build_dir),
            "--target", "run"
        ]

        if self.INTERACTIVE_CONSOLE:

            print("[ZephyrRunner] Launching interactive QEMU console...")

            subprocess.Popen(
                run_cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                env=env
            )

            # IMPORTANT:
            # Interactive mode does NOT return a process for profiling.
            # We return None to signal debug mode.
            return None

        else:

            print("[ZephyrRunner] Launching QEMU (deterministic mode)...")

            proc = subprocess.Popen(
                run_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )

            proc._obelisk_execution_model = "rtos"
            proc._obelisk_platform = "zephyr"

            return proc