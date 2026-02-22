# layer2/infer.py

def _eval_protected_mode(pm_evidence):
    """
    Decide whether protected mode is justified based on
    strength-weighted evidence.
    """
    strong = sum(1 for e in pm_evidence if e["strength"] == "strong")
    medium = sum(1 for e in pm_evidence if e["strength"] == "medium")
    weak = sum(1 for e in pm_evidence if e["strength"] == "weak")

    # Thresholds:
    # - any strong evidence
    # - or multiple corroborating weaker signals
    if strong >= 1:
        return True
    if medium >= 2:
        return True
    if weak >= 3:
        return True

    return False


def infer_requirements(scan, inspection, artifact):
    result = {
        "platforms": [],
        "cpu_class": {
            "minimum": "unknown",
            "confidence": 0.0
        },
        "memory_model": "unknown",
        "graphics": ["text"],
        "sound": [],
        "constraints": {},
        "negative": []
    }
    if scan.get("zephyr_prj", 0) > 0:
        result["platforms"] = [("rtos", 0.95)]
        result["constraints"]["requires_rtos_execution_contract"] = True
        result["negative"] = ["not_dos", "not_linux", "not_windows"]

        result["memory_model"] = "unknown"
        result["cpu_class"] = {
            "minimum": "unknown",
            "confidence": 0.3
        }

        result["sound"] = {
            "requirement": "optional",
            "devices": [],
            "confidence": 0.3
        }

        return result

    # 🔹 Phase 2.5 Linux short-circuit
    if "linux" in artifact.platforms_present:
        result["platforms"] = [("linux", 0.95)]
        result["negative"] = ["not_dos", "not_windows"]

        # Linux has no entry point; requires execution contract
        result["constraints"]["requires_linux_execution_contract"] = True

        result["sound"] = {
            "requirement": "absent",
            "devices": [],
            "confidence": 0.9
        }

        return result
    # --------------------------------------
    # Platform inference
    # --------------------------------------
    if inspection["pe_exe"]:
        result["platforms"].append(("windows", 0.9))
        result["platforms"].append(("dos", 0.1))
        result["negative"].extend(["not_dos", "not_linux"])
        return result

    # Default assumption: DOS primary
    result["platforms"].append(("dos", 0.85))
    result["platforms"].append(("windows", 0.15))
    result["negative"].append("not_linux")

    # --------------------------------------
    # CPU & memory inference
    # --------------------------------------
    pm_evidence = inspection.get("pm_evidence", [])
    result["sound"] = None

    if _eval_protected_mode(pm_evidence):
        # Protected mode implies >= 386
        result["memory_model"] = "protected"
        result["cpu_class"] = {
            "minimum": "386",
            "confidence": 0.7
        }
        result["constraints"]["requires_dos_extender"] = True
        result["negative"].append("not_windows_nt")

    else:
        # No protected-mode commitment
        result["memory_model"] = "unknown"
        result["constraints"]["requires_dos_extender"] = False

        # Very weak heuristic: large EXE implies >8086
        max_size = max(inspection.get("exe_sizes", {}).values(), default=0)

        if max_size > 300_000:
            result["cpu_class"] = {
                "minimum": "286",
                "confidence": 0.3
            }
        else:
            result["cpu_class"] = {
                "minimum": "8086",
                "confidence": 0.3
            }

    sound = infer_sound_profile(inspection)
    result["sound"] = sound

    if not result["platforms"]:
        result["platforms"] = []

    return result

def infer_sound_profile(inspection):
    hardware = inspection.get("sound_evidence", [])
    awareness = inspection.get("sound_awareness_evidence", [])

    # Case 1: no sound awareness at all
    if not hardware and not awareness:
        return {
            "requirement": "absent",
            "devices": [],
            "confidence": 0.9
        }

    # Case 2: sound-aware, but backend unknown
    if not hardware and awareness:
        return {
            "requirement": "optional",
            "devices": [],
            "confidence": 0.4
        }

    # Case 3: sound backend evidence exists
    return {
        "requirement": "optional",
        "devices": hardware,
        "confidence": 0.6
    }