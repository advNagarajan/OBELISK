from layer5.models import EvaluatedConfiguration


def satisfies_requirements(observation, requirements):
    violations = []

    for req in requirements:
        if req.status == "required":
            if not observation.features.get(req.feature):
                violations.append(f"{req.feature} required")

    return len(violations) == 0, violations


def score_configuration(observation):
    """
    Lower score = simpler config.
    Avoid overfitting to unstable signals.
    """

    score = 0.0

    if observation.features.get("video") == "svga":
        score += 1.0

    if observation.features.get("timing") == "adaptive":
        score += 0.5

    return score


def evaluate_configurations(observations, requirements):
    evaluated = []

    for obs in observations:
        ok, violations = satisfies_requirements(obs, requirements)

        score = score_configuration(obs) if ok else float("inf")

        evaluated.append(
            EvaluatedConfiguration(
                variant=obs.variant,
                emulator=obs.emulator,
                execution_class=obs.execution_class,
                stable=obs.stable,
                satisfies_requirements=ok,
                score=score,
                violations=violations,
            )
        )

    evaluated.sort(key=lambda c: (not c.stable, c.score))
    return evaluated


def select_canonical(evaluated):
    for cfg in evaluated:
        if cfg.stable and cfg.satisfies_requirements:
            return cfg
    return None