# layer5/compatibility.py

from collections import defaultdict
from layer5.models import CompatibilitySummary


def compute_compatibility(observations):
    grouped = defaultdict(list)

    for obs in observations:
        grouped[obs.emulator].append(obs)

    results = {}

    for emulator, obs_list in grouped.items():
        total = len(obs_list)
        stable = sum(1 for o in obs_list if o.stable)

        rate = stable / total if total > 0 else 0.0

        results[emulator] = CompatibilitySummary(
            total_runs=total,
            stable_runs=stable,
            stability_rate=round(rate, 3),
        )

    return results