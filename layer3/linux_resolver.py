from pathlib import Path
from layer3.linux_intent import LinuxExecutionIntent

def resolve_linux_intent(system_profile) -> LinuxExecutionIntent:
    contract = system_profile.linux_execution_contract
    if not contract:
        raise ValueError("Linux execution requires execution contract")

    artifact_root = Path(system_profile.artifact_root)

    # ----------------------------
    # Phase 2.5 Linux inference
    # ----------------------------

    # Case 1: single script artifact
    scripts = [
        f for f in artifact_root.iterdir()
        if f.is_file() and f.suffix in (".sh",)
    ]

    if len(scripts) == 1:
        script = scripts[0]
        exec_path = "/bin/busybox"
        exec_args = ["sh", f"/artifact/{script.name}"]

    else:
        raise NotImplementedError(
            "Linux execution inference supports single-script artifacts only (Phase 2.5)"
        )

    return LinuxExecutionIntent(
        kernel_path="vmlinuz",
        initramfs_path="initramfs-obelisk.img",

        exec_path=exec_path,
        exec_args=exec_args,

        memory_mb=512,
        timeout_ms=30000,

        console="serial",
        graphics="none",

        env={}
    )
