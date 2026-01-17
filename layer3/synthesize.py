from layer3.resolver import resolve_machine
from layer3.linux_resolver import resolve_linux_intent

from layer3.adapters.dosbox import DOSBoxAdapter
from layer3.adapters.qemu import QEMUAdapter
from layer3.adapters.linux_qemu import LinuxQEMUAdapter

ADAPTERS = [
    DOSBoxAdapter(),
    QEMUAdapter(),
    LinuxQEMUAdapter()
]

def synthesize(system_profile):

    plans = []

    if system_profile.execution_surface == "linux_contract":
        intent = resolve_linux_intent(system_profile)

        for adapter in ADAPTERS:
            if isinstance(adapter, LinuxQEMUAdapter):
                plans.extend(
                    adapter.generate_variants(intent, system_profile)
                )
    else:
        machine = resolve_machine(system_profile)

        for adapter in ADAPTERS:
            if adapter.supports(system_profile):
                plans.extend(
                    adapter.generate_variants(
                        machine,
                        system_profile
                    )
                )

    return sorted(plans, key=lambda p: p.priority)
