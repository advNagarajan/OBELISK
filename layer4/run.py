from layer4.runners.dosbox import DOSBoxRunner
from layer4.profiler import ExecutionProfiler
from layer4.runners.qemu import QEMURunner


def run_layer4(plans):
    profiler = ExecutionProfiler()
    profiles = []

    for plan in plans:
        if plan.emulator == "dosbox":
            runner = DOSBoxRunner()

        elif plan.emulator == "qemu":
            runner = QEMURunner()

        else:
            raise ValueError(f"Unknown emulator: {plan.emulator}")

        profiles.append(
            profiler.profile(plan, runner)
        )

    return profiles
