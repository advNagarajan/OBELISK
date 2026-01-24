def synthesize_qemu_args(config):
    args = []

    machine = config["machine"]

    CPU_CLASS_TO_QEMU = {
        "286": "486",      # closest usable
        "386": "486",      # safest baseline
        "486": "486",
        "pentium": "pentium",
    }

    cpu_class = machine.get("cpu", "486")
    qemu_cpu = CPU_CLASS_TO_QEMU.get(cpu_class, "486")

    args += [
        "-machine", "pc",
        "-cpu", qemu_cpu,
        "-m", str(machine["memory_mb"]),
    ]

    graphics = config.get("graphics", "vga")
    if graphics == "vga":
        args += ["-vga", "std"]

    sound = config.get("sound", [])
    if "sb16" in sound:
        args += ["-device", "sb16"]

    return args
