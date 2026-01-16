from layer3.canonical import CanonicalMachine

CPU_ORDER = ["8086", "286", "386", "486"]

def escalate_cpu(min_cpu: str) -> str:
    if min_cpu not in CPU_ORDER:
        return "386"
    i = CPU_ORDER.index(min_cpu)
    return CPU_ORDER[min(i + 1, len(CPU_ORDER) - 1)]


def resolve_machine(system_profile) -> CanonicalMachine:
    cpu_info = system_profile.cpu_class
    min_cpu = cpu_info.get("minimum", "286")

    cpu = (
        escalate_cpu(min_cpu)
        if cpu_info.get("confidence", 0) < 0.5
        else min_cpu
    )

    requires_ext = system_profile.constraints.get(
        "requires_dos_extender", False
    )

    memory_mb = 32 if requires_ext else 16
    dos_extender = requires_ext

    graphics = "vga"

    sound_profile = system_profile.sound

    if sound_profile is None:
        sound = []
        sound_required = False
    else:
        if sound_profile.requirement == "absent":
            sound = []
            sound_required = False
        else:
            if "sb16" in sound_profile.supported_devices:
                sound = ["sb16"]
            elif "adlib" in sound_profile.supported_devices:
                sound = ["adlib"]
            else:
                sound = []

            sound_required = (sound_profile.requirement == "required")

    return CanonicalMachine(
        cpu=cpu,
        memory_mb=memory_mb,
        graphics=graphics,
        sound=sound,
        sound_required=sound_required,
        dos_extender=dos_extender
    )
