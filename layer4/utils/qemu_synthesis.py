def synthesize_qemu_args(config: dict):
    """
    Deterministically translate Layer-3 QEMU config JSON
    into QEMU command-line arguments.

    Phase-2 scope (explicit):
      - FreeDOS guest
      - qemu-system-i386
      - Conservative defaults
      - No heuristics or fallbacks
    """

    args = []

    machine = config["machine"]

    # -------------------------------------------------
    # CPU (Phase-2 constraint)
    # -------------------------------------------------
    # QEMU does not provide a faithful 8086/286 model.
    # qemu32 is the minimum practical CPU model that
    # satisfies all DOS-era architectural requirements.
    args += ["-cpu", "qemu32"]

    # -------------------------------------------------
    # Memory (pure semantic mapping)
    # -------------------------------------------------
    mem_mb = machine["memory_mb"]
    args += ["-m", str(mem_mb)]

    # -------------------------------------------------
    # Graphics (conservative mapping)
    # -------------------------------------------------
    graphics = config.get("graphics", "vga")

    if graphics == "text":
        args += ["-nographic"]
    else:
        # Both vga and svga map to std VGA in Phase 2
        args += ["-vga", "std"]

    # -------------------------------------------------
    # Intentionally NOT synthesized in Phase 2:
    #   - sound devices
    #   - dos_extender semantics
    #   - machine type
    #   - timing / acceleration
    #   - QMP / monitoring
    #
    # These are introduced only after Phase 2 is frozen.
    # -------------------------------------------------

    return args
