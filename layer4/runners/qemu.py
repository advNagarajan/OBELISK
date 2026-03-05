# layer4/runners/qemu.py

import subprocess
import tempfile
import shutil
from pathlib import Path
import json

from config import QEMU_PATH, FREEDOS_IMG
from layer4.utils.qemu_synthesis import synthesize_qemu_args
from layer4.utils.initramfs_linux import build_initramfs

def windows_short_path(p: Path) -> str:
    import subprocess
    out = subprocess.check_output(
        ["cmd", "/c", "for %I in (\"" + str(p) + "\") do @echo %~sI"],
        text=True
    )
    return out.strip()

class QEMURunner:
    """
    Phase 2.5 QEMU runner.

    DOS:
      - Boots FreeDOS from system image
      - Uses per-run FAT directory as D:
      - Executes AUTOEXEC.BAT via FDAUTO.BAT

    Linux:
      - Kernel + initramfs (system boot model)
      - No entry point
      - Non-terminating execution
    """

    def launch(self, plan):
        print(">>> QEMURunner.launch() CALLED FROM:", __file__)

        # -----------------------------
        # Load Layer-3 config
        # -----------------------------
        with open(plan.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        storage = config.get("storage")

        # Linux does NOT require FAT / writable FS
        if "kernel" in config:
            pass

        else:
            # DOS path
            if not storage:
                raise ValueError("QEMU requires storage semantics")

            if storage.get("boot_disk") != "dos":
                raise NotImplementedError("DOS QEMU requires boot_disk = 'dos'")

            if storage.get("fs_type") != "fat":
                raise NotImplementedError("DOS QEMU requires FAT filesystem")

            if storage.get("writable_fs") is not True:
                raise NotImplementedError("DOS QEMU requires writable filesystem")

        # -----------------------------
        # Linux execution path
        # -----------------------------
        if plan.variant.startswith("linux"):

            # HARD GUARD: Linux has no entry point
            if getattr(plan, "entry_point", None):
                raise ValueError(
                    "Linux execution does not support entry_point "
                    "(system boot model)"
                )

            machine = config.get("machine", {})
            kernel_cfg = config["kernel"]

            kernel = Path(kernel_cfg["image"]).resolve()

            # --------------------------------------------------
            # Locate OBELISK root from config_path
            # --------------------------------------------------
            config_path = Path(plan.config_path).resolve()
            obelisk_root = None

            for parent in config_path.parents:
                if (parent / "runtime" / "linux").exists():
                    obelisk_root = parent
                    break

            if obelisk_root is None:
                raise RuntimeError(
                    "Could not locate OBELISK root (missing runtime/linux)"
                )

            runtime_linux = obelisk_root / "runtime" / "linux"
            runtime_linux.mkdir(parents=True, exist_ok=True)

            initramfs = runtime_linux / "initramfs.img"

            build_initramfs(
                project_root=Path.cwd(),
                artifact_path=Path(plan.artifact_root),
                entrypoint=config["artifact"]["entrypoint"],
                output_path=initramfs,
            )

            if not kernel.exists():
                raise FileNotFoundError(f"Kernel not found: {kernel}")
            if not initramfs.exists():
                raise FileNotFoundError(f"Initramfs not found: {initramfs}")

            artifact_root = Path(plan.artifact_root)
            if not artifact_root.exists():
                raise FileNotFoundError(f"Artifact root not found: {artifact_root}")

            # -----------------------------
            # QEMU command (Linux)
            # -----------------------------
            cmd = [
                r"C:\Program Files\qemu\qemu-system-x86_64.exe",
                "-machine", "pc",
                "-cpu", machine.get("cpu", "qemu64"),
                "-m", str(machine.get("memory_mb", 256)),
                "-vga", "std",
                "-kernel", str(kernel),
                "-initrd", str(initramfs),
                "-append", kernel_cfg.get(
                    "cmdline",
                    "console=tty0 console=ttyS0 panic=-1"
                ),
                "-no-reboot",
                # Serial is logged for observability; success is userspace reach,
                # not process exit.
                "-serial", "file:serial.log",
            ]

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Phase 2.5 Linux semantic markers
            proc._obelisk_execution_model = "system" # type: ignore
            proc._obelisk_platform = "linux" # type: ignore

            return proc

        # -----------------------------
        # DOS execution path (unchanged)
        # -----------------------------
        execution = config.get("execution", {})
        if not execution.get("autoexec", False):
            raise NotImplementedError("DOS execution requires autoexec")

        entry = execution.get("entry_point") or plan.entry_point
        if not entry:
            raise ValueError("DOS execution requires an entry point")

        src_root = Path(plan.artifact_root)
        entry = Path(entry).name.upper()

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

        # -----------------------------
        # Prepare per-run FAT D: drive
        # -----------------------------
        tmpdir = tempfile.TemporaryDirectory()
        run_dir = Path(tmpdir.name)

        print(">>> artifact_root =", src_root)
        print(">>> entry_dir =", entry_dir)
        print(">>> entry_dir == src_root ?", entry_dir == src_root)

        # Copy files into run_dir (D:)
        if entry_dir == src_root:
            print(">>> COPYING FLAT ARTIFACT INTO D:\\")
            for item in entry_dir.iterdir():
                if item.is_file():
                    shutil.copy(item, run_dir / item.name)
        else:
            print(">>> COPYING NESTED ARTIFACT INTO SUBDIR", entry_dir.name)
            shutil.copytree(entry_dir, run_dir / entry_dir.name)

        # -----------------------------
        # AUTOEXEC.BAT (classic logic)
        # -----------------------------
        lines = ["@ECHO OFF"]

        # Phase 2.5 addition: sound environment
        sound = config.get("sound", [])
        if "sb16" in sound:
            lines.append("SET BLASTER=A220 I7 D1 T6")

        lines.append("D:")

        if entry_dir != src_root:
            lines.append(f"CD {entry_dir.name}")

        lines.append("ECHO START > D:\\STARTED.TXT")
        lines.append(entry_name) # type: ignore
        lines.append("ECHO %ERRORLEVEL% > D:\\ERRLVL.TXT")
        lines.append("ECHO END > D:\\FINISH.TXT")

        autoexec = run_dir / "AUTOEXEC.BAT"
        autoexec.write_text("\n".join(lines) + "\n")

        # -----------------------------
        # QEMU command (original working shape)
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
            text=True,
        )

        # Keep temp directory alive
        proc._obelisk_tmpdir = tmpdir # type: ignore
        proc._obelisk_run_dir = run_dir # type: ignore

        return proc
