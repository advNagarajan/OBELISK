def find_entry_points(artifact):
    points = []

    # DOS-style entry points
    for f in artifact.files:
        name = f.path.lower()
        if name.endswith((".exe", ".com", ".bat")):
            points.append(f.path)

    # Linux Phase 2.5: /init is authoritative
    if artifact.has_init:
        points.append("init")

    return points
