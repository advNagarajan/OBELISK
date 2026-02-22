import subprocess
import shutil
import json
import sys
from pathlib import Path


class ZephyrRunner:

    def launch(self, plan):

        with open(plan.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        board = config["board"]
        source_root = Path(config["source_root"]).resolve()

        if not source_root.exists():
            raise FileNotFoundError(
                f"Zephyr source_root not found: {source_root}"
            )

        # ------------------------------------------
        # CLEAN BUILD (deterministic)
        # ------------------------------------------
        build_dir = source_root / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir)

        # ------------------------------------------
        # Step 1: Build
        # ------------------------------------------
        build_cmd = [
            sys.executable,
            "-m",
            "west",
            "build",
            "-b", board,
            "."
        ]

        subprocess.run(
            build_cmd,
            cwd=source_root,
            check=True
        )

        # ------------------------------------------
        # Step 2: Run
        # ------------------------------------------
        run_cmd = [
            sys.executable,
            "-m",
            "west",
            "build",
            "-t", "run"
        ]

        proc = subprocess.Popen(
            run_cmd,
            cwd=source_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        proc._obelisk_execution_model = "rtos"
        proc._obelisk_platform = "zephyr"

        return proc