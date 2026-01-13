from layer4.runners.dosbox import DOSBoxRunner
from layer4.runners.pcem import PCemRunner
from layer4.profiler import ExecutionProfiler


def run_layer4(plans):
    profiler = ExecutionProfiler()
    profiles = []

    for plan in plans:
        if plan.emulator == "dosbox":
            runner = DOSBoxRunner()

        elif plan.emulator == "pcem":
            runner = PCemRunner()

        else:
            raise ValueError(f"Unknown emulator: {plan.emulator}")

        profiles.append(
            profiler.profile(plan, runner)
        )

    return profiles
