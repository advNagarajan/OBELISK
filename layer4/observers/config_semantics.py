def parse_dosbox_config(conf_path):
    semantics = {
        "timing_mode": "unknown",
        "sound_enabled": False,
        "graphics_mode": "unknown"
    }

    try:
        text = open(conf_path, "r", errors="ignore").read().lower()
    except Exception:
        return semantics

    # Timing
    if "cycles=auto" in text:
        semantics["timing_mode"] = "adaptive"
    elif "cycles=" in text:
        semantics["timing_mode"] = "fixed"

    # Sound
    if "sbtype=" in text and "sbtype=none" not in text:
        semantics["sound_enabled"] = True

    # Graphics
    if "svga" in text:
        semantics["graphics_mode"] = "svga"
    elif "vga" in text:
        semantics["graphics_mode"] = "vga"

    return semantics

def validate_linux_config(config: dict) -> None:
    """
    Validate Linux Phase 2.5 execution semantics.

    Linux does NOT use:
    - entry_point
    - storage / disks
    - mounts
    - kernel.initramfs (synthesized by L4)
    """

    if "kernel" not in config or "image" not in config["kernel"]:
        raise ValueError("Linux config requires kernel.image")

    if "artifact" not in config:
        raise ValueError("Linux config requires artifact section")

    if "entrypoint" not in config["artifact"]:
        raise ValueError("Linux artifact requires entrypoint")

    # Explicitly forbid DOS-style fields
    forbidden = ["entry_point", "storage", "mounts"]
    for field in forbidden:
        if field in config:
            raise ValueError(f"Linux config must not define '{field}'")

    if "initramfs" in config.get("kernel", {}):
        raise ValueError("Linux kernel.initramfs must not be specified (L4 synthesizes it)")
