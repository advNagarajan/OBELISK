# layer4/runners/qemu.py

import subprocess
import tempfile
import shutil
from pathlib import Path
from layer4.utils.qemu_synthesis import synthesize_qemu_args
import json

from config import QEMU_PATH, FREEDOS_IMG


class QEMURunner:
    """
    Phase 2 QEMU runner.
    Responsibility:
      - Boot FreeDOS
      - Mount a writable FAT C: drive
      - Execute AUTOEXEC.BAT
    """

    def launch(self, plan):
        print(">>> QEMURunner.launch() CALLED FROM:", __file__)
        # -----------------------------
        # Load Layer-3 config (authoritative)
        # -----------------------------
        with open(plan.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # -----------------------------
        # Validate storage semantics
        # -----------------------------
        storage = config.get("storage")
        if not storage:
            raise ValueError("QEMU Phase 2 requires storage semantics")

        if storage.get("boot_disk") != "dos":
            raise NotImplementedError("QEMU Phase 2 supports only DOS boot")

        if storage.get("fs_type") != "fat":
            raise NotImplementedError("QEMU Phase 2 requires FAT filesystem")

        if storage.get("writable_fs") is not True:
            raise NotImplementedError("QEMU Phase 2 requires writable filesystem")

        # -----------------------------
        # Prepare per-run FAT C: drive
        # -----------------------------
        tmpdir = tempfile.TemporaryDirectory()
        run_dir = Path(tmpdir.name)

        # -----------------------------
        # Execution semantics
        # -----------------------------
        execution = config.get("execution", {})
        if not execution.get("autoexec", False):
            raise NotImplementedError("QEMU Phase 2 requires autoexec execution")

        entry = execution.get("entry_point")
        if not entry:
            raise ValueError("QEMU Phase 2 requires an entry_point")
        
        src_root = Path(plan.artifact_root)
        entry = execution["entry_point"]

        candidates = [entry]
        if "." not in entry:
            candidates += [entry + ".EXE", entry + ".COM", entry + ".BAT"]

        entry_dir = None
        entry_name = None

        # Case A: flat artifact
        for name in candidates:
            if (src_root / name).exists():
                entry_dir = src_root
                entry_name = name
                break

        # Case B: nested artifact
        if entry_dir is None:
            for sub in src_root.iterdir():
                if not sub.is_dir():
                    continue
                for name in candidates:
                    if (sub / name).exists():
                        entry_dir = sub
                        entry_name = name
                        break
                if entry_dir:
                    break

        if entry_dir is None:
            raise FileNotFoundError(
                f"Entry point {entry} not found under artifact_root {src_root}"
            )

        print(">>> artifact_root =", src_root)
        print(">>> entry_dir =", entry_dir)
        print(">>> entry_dir == src_root ?", entry_dir == src_root)
        # Copy files into C:\
        if entry_dir == src_root:
            # Flat artifact → copy files directly into C:\
            print(">>> COPYING FLAT ARTIFACT INTO C:\\")
            for item in entry_dir.iterdir():
                if item.is_file():
                    print(">>> copying file", item.name)
                    shutil.copy(item, run_dir / item.name)
        else:
            print(">>> COPYING NESTED ARTIFACT INTO SUBDIR", entry_dir.name)
            # Nested artifact → preserve subdirectory
            dst = run_dir / entry_dir.name
            shutil.copytree(entry_dir, dst)

        print(">>> C:\\ contents after copy:")
        for p in run_dir.iterdir():
            print("   ", p.name, "(dir)" if p.is_dir() else "(file)")

        lines = []
        lines.append("@ECHO OFF")
        lines.append("D:")

        if entry_dir != src_root:
            lines.append(f"CD {entry_dir.name}")

        lines.append("echo START > D:\\STARTED.TXT")
        lines.append(entry_name)
        lines.append("echo %ERRORLEVEL% > D:\\ERRLVL.TXT")
        lines.append("echo END > D:\\FINISH.TXT")

        autoexec = run_dir / "AUTOEXEC.BAT"
        autoexec.write_text("\n".join(lines) + "\n")

        # -----------------------------
        # Synthesize QEMU command
        # -----------------------------
        cmd = [
            QEMU_PATH,
            *synthesize_qemu_args(config),
            "-drive", f"file={FREEDOS_IMG},format=raw,if=ide",
            "-drive", f"file=fat:rw:{run_dir},format=raw",
            "-boot", "c",
            "-no-reboot",
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Keep temp directory alive
        proc._obelisk_tmpdir = tmpdir
        proc._obelisk_run_dir = run_dir

        return proc
