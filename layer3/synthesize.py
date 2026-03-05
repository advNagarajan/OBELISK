from layer3.resolver import resolve_machine
from layer3.linux_resolver import resolve_linux_intent

from layer3.adapters.dosbox import DOSBoxAdapter
from layer3.adapters.qemu import QEMUAdapter
from layer3.adapters.linux_qemu import LinuxQEMUAdapter
from layer3.rtos_resolver import resolve_rtos_intent
from layer3.adapters.zephyr import ZephyrAdapter

ADAPTERS = [
    DOSBoxAdapter(),
    QEMUAdapter(),
    LinuxQEMUAdapter(),
    ZephyrAdapter()
]

from pathlib import Path

PREFERRED_MAIN_NAMES = {
    "main", "run", "game", "app",
    "doom", "mario", "nibbles", "tc"
}

UTILITY_NAMES = {
    "make", "tlink", "tlib", "bgobj",
    "grep", "touch", "cpp", "objxref"
}


def _score_entry(path: str):
    name = Path(path).stem.lower()
    score = 0

    # prefer likely main executables
    if name in PREFERRED_MAIN_NAMES:
        score += 100

    # penalize utilities
    if name in UTILITY_NAMES:
        score -= 50

    # shorter names often mean main programs
    score -= len(name)

    return score

def synthesize(system_profile):

    # --- ENTRYPOINT HEURISTIC ---
    if getattr(system_profile, "entry_points", None):
        system_profile.entry_points.sort(
            key=lambda e: _score_entry(e.path),
            reverse=True
        )

    plans = []
    if system_profile.execution_surface in (
        "rtos_project",
        "rtos_wrapped"
    ):
        intent = resolve_rtos_intent(system_profile)

        for adapter in ADAPTERS:
            if isinstance(adapter, ZephyrAdapter):
                plans.extend(
                    adapter.generate_variants(intent, system_profile)
                )

        return plans

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
