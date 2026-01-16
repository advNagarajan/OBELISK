from layer3.linux_intent import LinuxExecutionIntent

DEFAULT_KERNEL = "vmlinuz"
DEFAULT_INITRAMFS = "initramfs.cpio.gz"

def resolve_linux_intent(system_profile) -> LinuxExecutionIntent:

    if system_profile.execution_surface == "linux_init":
        mode = "init"
        initramfs = system_profile.artifact_root

    elif system_profile.execution_surface == "linux_program":
        mode = "program"
        initramfs = "generated"   # Layer 4 will build it

    elif system_profile.execution_surface == "boot_disk":
        mode = "boot"
        initramfs = ""

    else:
        raise ValueError("Unsupported Linux execution surface")

    return LinuxExecutionIntent(
        kernel_path=DEFAULT_KERNEL,
        initramfs_path=initramfs,

        mode=mode,
        entry_point="/init",

        memory_mb=64,
        timeout_ms=30000,

        graphics="none",
        console="serial",

        env={},
        arguments=[]
    )
