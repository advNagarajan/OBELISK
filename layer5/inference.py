from collections import Counter
from layer5.models import InferredRequirement


# ============================================================
# Helpers
# ============================================================

def _relevant_observations(observations, feature_name):
    """
    Return only observations where the feature is explicitly defined.
    This prevents cross-emulator pollution (e.g., Zephyr has no sound/video).
    """
    return [
        obs for obs in observations
        if obs.features.get(feature_name) is not None
    ]


# ============================================================
# Boolean Feature Inference
# ============================================================

def infer_boolean_feature(observations, feature_name: str) -> InferredRequirement:
    """
    Infer requirement status for boolean feature.
    Conservative: requires meaningful cross-configuration variation.
    """

    relevant = _relevant_observations(observations, feature_name)

    # If feature never appears (e.g., Zephyr + sound)
    if not relevant:
        return InferredRequirement(
            feature=feature_name,
            status="unknown",
            confidence=0.0,
            evidence=["feature not applicable in observed environments"],
        )

    stable_with = 0
    stable_without = 0

    for obs in relevant:
        value = obs.features.get(feature_name)

        if obs.stable:
            if value:
                stable_with += 1
            else:
                stable_without += 1

    evidence = []
    status = "unknown"
    confidence = 0.0

    total_stable = stable_with + stable_without

    # If no stable runs among relevant observations
    if total_stable == 0:
        return InferredRequirement(
            feature=feature_name,
            status="unknown",
            confidence=0.0,
            evidence=["no stable executions for applicable configurations"],
        )

    # Only infer strong claims if multiple configurations exist
    if len(relevant) > 1:

        if stable_with > 0 and stable_without == 0:
            status = "required"
            confidence = 0.9
            evidence.append(f"{feature_name} present in all stable runs")

        elif stable_with > 0 and stable_without > 0:
            status = "optional"
            confidence = 0.8
            evidence.append(
                f"stable runs observed with and without {feature_name}"
            )

        elif stable_with == 0 and stable_without > 0:
            status = "forbidden"
            confidence = 0.8
            evidence.append(f"{feature_name} absent in all stable runs")

    # If only one configuration exists, do not overclaim
    else:
        status = "unknown"
        confidence = 0.3
        evidence.append("insufficient configuration diversity for inference")

    return InferredRequirement(
        feature=feature_name,
        status=status,
        confidence=confidence,
        evidence=evidence,
    )


# ============================================================
# Categorical Feature Inference
# ============================================================

def infer_categorical_feature(observations, feature_name: str) -> InferredRequirement:
    """
    Infer preference for categorical feature (e.g., video, timing).
    Conservative and emulator-aware.
    """

    relevant = _relevant_observations(observations, feature_name)

    if not relevant:
        return InferredRequirement(
            feature=feature_name,
            status="unknown",
            confidence=0.0,
            evidence=["feature not applicable in observed environments"],
        )

    values = [
        obs.features.get(feature_name)
        for obs in relevant
        if obs.stable
    ]

    if not values:
        return InferredRequirement(
            feature=feature_name,
            status="unknown",
            confidence=0.0,
            evidence=["no stable executions for applicable configurations"],
        )

    counter = Counter(values)

    # Only infer strong preference if multiple configurations exist
    if len(counter) == 1 and len(relevant) > 1:
        value = next(iter(counter))
        return InferredRequirement(
            feature=feature_name,
            status="preferred",
            confidence=0.9,
            evidence=[f"all stable runs used {value}"],
            preferred_value=value,
        )

    if len(counter) > 1:
        return InferredRequirement(
            feature=feature_name,
            status="optional",
            confidence=0.7,
            evidence=[
                f"stable runs observed with multiple {feature_name} values"
            ],
        )

    # Only one configuration available → insufficient diversity
    return InferredRequirement(
        feature=feature_name,
        status="unknown",
        confidence=0.3,
        evidence=["insufficient configuration diversity for inference"],
    )


# ============================================================
# Entry Point
# ============================================================

def infer_all_requirements(observations):
    requirements = []

    requirements.append(infer_boolean_feature(observations, "sound"))
    requirements.append(infer_categorical_feature(observations, "video"))
    requirements.append(infer_categorical_feature(observations, "timing"))

    return requirements