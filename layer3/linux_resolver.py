from pathlib import Path
from layer3.linux_intent import LinuxExecutionIntent

def is_elf_binary(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            magic = f.read(4)
            return magic == b"\x7fELF"
    except Exception:
        return False


def resolve_linux_intent(system_profile) -> LinuxExecutionIntent:
    artifact_root = Path(system_profile.artifact_root)

    # -------------------------------------------------
    # Phase 2.5: locate candidate artifact entrypoints
    # -------------------------------------------------
    files = [
        f for f in artifact_root.iterdir()
        if f.is_file()
    ]

    if not files:
        raise RuntimeError(
            "Linux artifact directory contains no executable files"
        )

    # Prefer common entrypoint names if present
    preferred_names = [
        "main",
        "run",
        "start",
        "app",
        "script"
    ]

    entry = None

    for name in preferred_names:
        for f in files:
            if f.stem.lower() == name:
                entry = f
                break
        if entry:
            break

    if entry is None:
        entry = files[0]

    # -------------------------------------------------
    # Determine execution wrapper
    # -------------------------------------------------

    if entry.suffix == ".sh":
        exec_path = "/bin/sh"
        exec_args = [f"/artifact/{entry.name}"]

    elif entry.suffix == ".py":
        exec_path = "/usr/bin/python3"
        exec_args = [f"/artifact/{entry.name}"]

    elif is_elf_binary(entry):
        # native executable
        exec_path = f"/artifact/{entry.name}"
        exec_args = []

    else:
        # fallback: treat as shell script
        exec_path = "/bin/sh"
        exec_args = [f"/artifact/{entry.name}"]

    # -------------------------------------------------
    # Canonical kernel (platform-owned)
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Construct execution intent
    # -------------------------------------------------

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