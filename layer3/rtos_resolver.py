from pathlib import Path
from layer3.rtos_intent import RTOSExecutionIntent
import shutil
import re

def rewrite_main_to_legacy(root: Path):

    rewritten = False

    for file in root.rglob("*.c"):

        try:
            text = file.read_text(errors="ignore")

            # match: int main(...)
            new_text, count = re.subn(
                r'\bint\s+main\s*\(',
                'int legacy_main(',
                text,
                count=1
            )

            if count > 0:
                file.write_text(new_text)
                rewritten = True
                break

        except Exception:
            continue

    return rewritten

# -------------------------------------------------
# Board Inference
# -------------------------------------------------

def _infer_board_from_source(root: Path):
    prj = root / "prj.conf"

    if prj.exists():
        text = prj.read_text(errors="ignore").lower()

        if "arm" in text or "cortex" in text:
            return "qemu_cortex_m3", 0.7, "prj.conf contains ARM hint"

        if "x86" in text:
            return "qemu_x86", 0.7, "prj.conf contains x86 hint"

    for file in root.rglob("*.c"):
        try:
            data = file.read_text(errors="ignore").lower()

            if "__asm__" in data and "eax" in data:
                return "qemu_x86", 0.5, "inline asm x86 register"

            if "__asm__" in data and "r0" in data:
                return "qemu_cortex_m3", 0.5, "inline asm ARM register"
        except Exception:
            continue

    return "qemu_x86", 0.2, "fallback baseline"


# -------------------------------------------------
# Project Detection
# -------------------------------------------------

def _is_zephyr_project(root: Path) -> bool:
    return (
        (root / "prj.conf").exists()
        and (root / "CMakeLists.txt").exists()
    )


# -------------------------------------------------
# Wrapper Safety Check
# -------------------------------------------------

def _has_legacy_main(root: Path) -> bool:
    """
    Require explicit contract:
    int legacy_main(void);
    """
    for file in root.rglob("*.c"):
        try:
            text = file.read_text(errors="ignore")
            if "legacy_main(" in text:
                return True
        except Exception:
            continue
    return False


# -------------------------------------------------
# Resolver
# -------------------------------------------------

def resolve_rtos_intent(system_profile) -> RTOSExecutionIntent:

    root = Path(system_profile.artifact_root)

    system_profile.execution_evidence.setdefault("rtos_resolution", {})

    # =================================================
    # Case 1: Native Zephyr project
    # =================================================
    if _is_zephyr_project(root):

        board, confidence, reason = _infer_board_from_source(root)

        evidence = {
            "mode": "native",
            "board_candidate": board,
            "confidence": confidence,
            "reason": reason,
            "wrapper_generated": False,
        }

        # Deterministic fallback
        if confidence < 0.5:
            evidence["fallback"] = True
            board = "qemu_x86"

        system_profile.execution_evidence["rtos_resolution"] = evidence

        return RTOSExecutionIntent(
            board=board,
            source_root=str(root),
            wrapper_generated=False,
            wrapper_root=None,
            timeout_ms=20000
        )

    # =================================================
    # Case 2: Wrapper mediation
    # =================================================

    c_files = [f for f in root.rglob("*.c") if "layer3_zephyr_wrapper" not in str(f)]

    if not c_files:
        raise RuntimeError(
            "RTOS wrapping requires C source files"
        )

    # Enforce explicit symbol contract
    if not _has_legacy_main(root):

        rewritten = rewrite_main_to_legacy(root)

        if not rewritten:
            raise RuntimeError(
                "No entrypoint found: expected main() or legacy_main()"
            )

    wrapper_root = root / "layer3_zephyr_wrapper"
    if wrapper_root.exists():
        shutil.rmtree(wrapper_root)

    wrapper_root.mkdir()
    artifact_dir = wrapper_root / "artifact"
    artifact_dir.mkdir(exist_ok=True)

    for f in c_files:
        shutil.copy(f, artifact_dir / f.name)

    # --------------------------
    # Zephyr scaffold
    # --------------------------

    (wrapper_root / "prj.conf").write_text(
        "CONFIG_PRINTK=y\n"
    )

    (wrapper_root / "CMakeLists.txt").write_text(
        "cmake_minimum_required(VERSION 3.20.0)\n"
        "find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})\n"
        "project(wrapper)\n"
        "\n"
        "file(GLOB LEGACY_SRC artifact/*.c)\n"
        "\n"
        "target_sources(app PRIVATE\n"
        "    src/main.c\n"
        "    ${LEGACY_SRC}\n"
        ")\n"
    )
    src_dir = wrapper_root / "src"
    src_dir.mkdir(exist_ok=True)

    (src_dir / "main.c").write_text(
        """
#include <zephyr/kernel.h>

extern int legacy_main(void);

void main(void) {
    printk("OBELISK WRAPPER START\\n");
    legacy_main();
    printk("OBELISK WRAPPER END\\n");
}
"""
    )

    # --------------------------
    # Board inference
    # --------------------------

    board, confidence, reason = _infer_board_from_source(root)

    evidence = {
        "mode": "wrapper",
        "board_candidate": board,
        "confidence": confidence,
        "reason": reason,
        "wrapper_generated": True,
        "wrapper_root": str(wrapper_root),
    }

    if confidence < 0.5:
        evidence["fallback"] = True
        board = "qemu_x86"

    system_profile.execution_evidence["rtos_resolution"] = evidence

    return RTOSExecutionIntent(
        board=board,
        source_root=str(wrapper_root),
        wrapper_generated=True,
        wrapper_root=str(wrapper_root),
        timeout_ms=20000
    )