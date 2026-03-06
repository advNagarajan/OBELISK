# layer5/run.py

import json
from pathlib import Path
from dataclasses import asdict

from layer5.analysis import analyze_all
from layer5.inference import infer_all_requirements
from layer5.selection import evaluate_configurations, select_canonical
from layer5.compatibility import compute_compatibility
from layer5.explanation import build_explanation
from layer5.models import Layer5Result


def run_layer5(execution_profiles, output_dir="layer5_output"):

    observations = analyze_all(execution_profiles)

    requirements = infer_all_requirements(observations)

    evaluated = evaluate_configurations(observations, requirements)

    canonical = select_canonical(evaluated)

    if canonical is None:
        compatibility = compute_compatibility(observations)

        explanation = (
            "No configuration achieved stable execution. "
            "Artifact appears incompatible with all reconstructed environments."
        )

        result = Layer5Result(
            chosen_variant=None,
            inferred_requirements=requirements,
            ranked_variants=evaluated,
            compatibility_by_emulator=compatibility,
            explanation=explanation,
        )

        out_dir = Path(output_dir)
        out_dir.mkdir(exist_ok=True)

        out_file = out_dir / "artifact_result.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(asdict(result), f, indent=2)

        return result

    compatibility = compute_compatibility(observations)

    explanation = build_explanation(
        canonical,
        requirements,
        compatibility
    )

    result = Layer5Result(
        chosen_variant=canonical.variant,
        inferred_requirements=requirements,
        ranked_variants=evaluated,
        compatibility_by_emulator=compatibility,
        explanation=explanation,
    )

    out_dir = Path(output_dir)
    out_dir.mkdir(exist_ok=True)

    out_file = out_dir / "artifact_result.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(asdict(result), f, indent=2)

    return result