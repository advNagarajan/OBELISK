# layer5/explanation.py

def build_explanation(canonical, requirements, compatibility):
    lines = []

    lines.append(
        f"Selected configuration '{canonical.variant}' "
        f"({canonical.emulator}) achieved stable execution."
    )

    for req in requirements:
        if req.status == "required":
            lines.append(
                f"{req.feature.capitalize()} support appears required for stability."
            )
        elif req.status == "preferred":
            lines.append(
                f"{req.feature.capitalize()} shows a consistent stable preference."
            )

    lines.append("Observed stability rates by emulator:")

    for emulator, summary in compatibility.items():
        lines.append(
            f"{emulator}: {summary.stable_runs}/{summary.total_runs} "
            f"stable ({summary.stability_rate})"
        )

    return " ".join(lines)