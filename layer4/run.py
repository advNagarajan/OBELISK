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

        elif plan.emulator == "zephyr":
            from layer4.runners.zephyr import ZephyrRunner
            runner = ZephyrRunner()
        else:
            raise ValueError(f"Unknown emulator: {plan.emulator}")

        profile = profiler.profile(plan, runner)

        if profile.execution_mode == "SYSTEM":
            assert profile.phases.get("stability_window_reached", False), \
                "SYSTEM execution did not reach stable state"

        profiles.append(profile)
    return profiles
