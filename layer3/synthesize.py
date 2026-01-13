from layer3.resolver import resolve_machine
from layer3.adapters.dosbox import DOSBoxAdapter
from layer3.adapters.qemu import QEMUAdapter

ADAPTERS = [
    DOSBoxAdapter(),
    QEMUAdapter()
]

def synthesize(system_profile):
    machine = resolve_machine(system_profile)
    plans = []

    for adapter in ADAPTERS:
        if adapter.supports(system_profile):
            plans.extend(
                adapter.generate_variants(
                    machine,
                    system_profile
                )
            )

    return sorted(plans, key=lambda p: p.priority)
