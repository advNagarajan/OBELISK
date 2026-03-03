# layer5/inference.py

from collections import Counter
from layer5.models import InferredRequirement


def infer_boolean_feature(observations, feature_name: str) -> InferredRequirement:
    stable_with = 0
    stable_without = 0

    for obs in observations:
        value = obs.features.get(feature_name)

        if obs.stable:
            if value:
                stable_with += 1
            else:
                stable_without += 1

    evidence = []
    status = "unknown"
    confidence = 0.0

    if stable_with > 0 and stable_without == 0:
        status = "required"
        confidence = 0.9
        evidence.append(f"{feature_name} present in all stable runs")

    elif stable_with > 0 and stable_without > 0:
        status = "optional"
        confidence = 0.8
        evidence.append(f"stable runs observed with and without {feature_name}")

    elif stable_with == 0 and stable_without > 0:
        status = "forbidden"
        confidence = 0.8
        evidence.append(f"{feature_name} absent in all stable runs")

    return InferredRequirement(
        feature=feature_name,
        status=status,
        confidence=confidence,
        evidence=evidence,
    )


def infer_categorical_feature(observations, feature_name: str) -> InferredRequirement:
    values = [
        obs.features.get(feature_name)
        for obs in observations
        if obs.stable and obs.features.get(feature_name) is not None
    ]

    if not values:
        return InferredRequirement(
            feature=feature_name,
            status="unknown",
            confidence=0.0,
            evidence=["no stable executions"],
        )

    counter = Counter(values)

    if len(counter) == 1:
        value = next(iter(counter))
        return InferredRequirement(
            feature=feature_name,
            status="preferred",
            confidence=0.9,
            evidence=[f"all stable runs used {value}"],
            preferred_value=value,
        )

    return InferredRequirement(
        feature=feature_name,
        status="optional",
        confidence=0.7,
        evidence=[f"stable runs observed with multiple {feature_name} values"],
    )


def infer_all_requirements(observations):
    requirements = []

    requirements.append(infer_boolean_feature(observations, "sound"))
    requirements.append(infer_categorical_feature(observations, "video"))
    requirements.append(infer_categorical_feature(observations, "timing"))

    return requirements