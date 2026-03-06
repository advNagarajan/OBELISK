from layer5.models import ExecutionObservation


def classify_execution(profile) -> str:
    """
    Conservative classification based on Layer 4 phases.
    We avoid making strong assumptions due to imperfect markings.
    """

    phases = profile.phases or {}

    emulator_started = phases.get("emulator_started", False)
    control = phases.get("control_transferred", False)
    stable_window = phases.get("stability_window_reached", False)

    if not emulator_started:
        return "failed"

    # Stable only if BOTH control transferred and stability reached
    if control and stable_window:
        return "stable"

    # Partial if control transferred but stability not confirmed
    if control and not stable_window:
        return "partial"

    return "failed"


def analyze_execution(profile) -> ExecutionObservation:
    """
    Normalize Layer 4 ExecutionProfile into conservative observation.
    """

    execution_class = classify_execution(profile)

    stable = execution_class == "stable"

    features = {
        "sound": profile.config.get("sound_enabled"),
        "video": profile.config.get("graphics_mode"),
        "timing": profile.config.get("timing_mode"),
    }

    return ExecutionObservation(
        emulator=profile.emulator,
        variant=profile.variant,
        entry_point=profile.entry_point,
        execution_class=execution_class,
        stable=stable,
        features=features,
        sound_outcome=profile.sound_outcome,
        host_telemetry=profile.host_telemetry or {},
    )


def analyze_all(profiles):
    return [analyze_execution(p) for p in profiles]