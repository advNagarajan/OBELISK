from layer2.models import SystemProfile, PlatformCandidate, EntryPoint, SoundProfile

def entry_confidence(path, inspection):
    score = 0.3

    size = inspection.get("exe_sizes", {}).get(path, 0)
    if size > 300_000:
        score += 0.4

    name = path.lower()
    if not any(k in name for k in ["setup", "readme", "install", "config"]):
        score += 0.2

    return min(score, 0.95)


def synthesize(artifact, scan, candidates, inspection, inference):
    # --------------------------------------
    # Platform candidates
    # --------------------------------------
    platforms = [
        PlatformCandidate(platform=p, confidence=c)
        for p, c in inference["platforms"]
    ]

    # --------------------------------------
    # Execution surface (backend-neutral)
    # --------------------------------------
    if artifact.disk_image or artifact.bootable:
        execution_surface = "boot_disk"

    elif inference["constraints"].get("requires_rtos_execution_contract"):
        execution_surface = "rtos_project"

    elif inference["constraints"].get("requires_linux_execution_contract"):
        execution_surface = "linux_contract"

    elif candidates:
        execution_surface = "dos_program"

    elif not inference["platforms"]:
        execution_surface = "baremetal"

    else:
        execution_surface = "unknown"

    # --------------------------------------
    # Entry points
    # --------------------------------------
    if execution_surface == "dos_program":
        entry_points = [
            EntryPoint(
                path=p,
                confidence=entry_confidence(p, inspection)
            )
            for p in candidates
        ]
    else:
        entry_points = []

    # --------------------------------------
    # Evidence (audit trail)
    # --------------------------------------
    evidence = {
        "pm_evidence": inspection.get("pm_evidence", []),
        "graphics_evidence": inspection.get("graphics_evidence", []),
        "sound_evidence": inspection.get("sound_evidence", [])
    }

    # --------------------------------------
    # Execution-relevant evidence
    # --------------------------------------
    execution_evidence = {}

    if inference["memory_model"] == "protected":
        execution_evidence["requires_386+"] = list({
            e["file"] for e in inspection.get("pm_evidence", [])
        })

    sound_profile = SoundProfile(
        requirement=inference["sound"]["requirement"],
        supported_devices=inference["sound"]["devices"],
        confidence=inference["sound"]["confidence"],
        evidence=inspection.get("sound_evidence", [])
    )

    linux_execution_contract = None

    if execution_surface == "linux_contract":
        linux_execution_contract = {
            "interface": "exec+args",
            "executor": "init"
        }

    return SystemProfile(
        artifact_root=artifact.normalized_path,
        platform_candidates=platforms,

        cpu_class=inference["cpu_class"],
        memory_model=inference["memory_model"],

        graphics=["text"],
        sound=sound_profile,

        graphics_evidence=inspection.get("graphics_evidence", []),
        sound_evidence=inspection.get("sound_evidence", []),

        entry_points=entry_points,

        constraints=inference["constraints"],
        negative_constraints=inference["negative"],

        evidence=evidence,
        execution_evidence=execution_evidence,

        execution_surface=execution_surface,
        linux_execution_contract=linux_execution_contract
    )
