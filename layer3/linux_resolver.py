from pathlib import Path
from layer3.linux_intent import LinuxExecutionIntent


def resolve_linux_intent(system_profile) -> LinuxExecutionIntent:
    artifact_root = Path(system_profile.artifact_root)

    # ----------------------------
    # Phase 2.5: single-script Linux
    # ----------------------------
    scripts = [
        f for f in artifact_root.iterdir()
        if f.is_file() and f.suffix == ".sh"
    ]

    if len(scripts) != 1:
        raise NotImplementedError(
            "Phase 2.5 Linux supports exactly one shell script artifact"
        )

    script = scripts[0]

    exec_path = "/bin/busybox"
    exec_args = ["sh", f"/artifact/{script.name}"]

    # ----------------------------
    # Canonical kernel (platform-owned)
    # ----------------------------
    kernel_path = (
        Path(__file__)
        .resolve()
        .parents[1]      # → OBELISK root
        / "runtime"
        / "linux"
        / "vmlinuz-virt"
    )

    if not kernel_path.exists():
        raise FileNotFoundError(
            f"Linux kernel not found at {kernel_path}"
        )

    return LinuxExecutionIntent(
        kernel_path=str(kernel_path),
        exec_path=exec_path,
        exec_args=exec_args,
        memory_mb=512,
        timeout_ms=30000,
        console="serial",
        graphics="none",
        env={}
    )
