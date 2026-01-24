import subprocess
from pathlib import Path


def build_initramfs(
    project_root: Path,
    artifact_path: Path,
    entrypoint: str,
    output_path: Path,
) -> None:
    """
    Build Linux initramfs via WSL (MANDATORY on Windows).

    This function only orchestrates.
    All Linux filesystem work happens inside WSL.
    """

    wsl_script = (
        project_root
        / "runtime"
        / "linux"
        / "wsl_build_initramfs.py"
    )

    if not wsl_script.exists():
        raise RuntimeError(f"Missing WSL builder: {wsl_script}")

    alpine_root = (
        project_root
        / "runtime"
        / "linux"
        / "alpine_root"
    )

    if not alpine_root.exists():
        raise RuntimeError(f"Missing alpine_root: {alpine_root}")

    # Convert Windows paths → WSL-visible paths
    def to_wsl(p: Path) -> str:
        """
        Convert an absolute Windows path to a WSL-visible path.
        If the path is already relative or non-Windows, return as-is.
        """
        if not p.drive:
            # Already relative or already WSL-style
            return str(p)

        drive = p.drive.rstrip(":").lower()
        rest = p.as_posix().split(":", 1)[1]
        return f"/mnt/{drive}{rest}"

    cmd = [
        "wsl",
        "python3",
        to_wsl(wsl_script.resolve()),
        to_wsl(alpine_root.resolve()),
        to_wsl(artifact_path.resolve()),
        entrypoint,
        to_wsl(output_path.resolve()),
    ]

    subprocess.run(cmd, check=True)

    if not output_path.exists():
        raise RuntimeError(
            f"initramfs build failed: output not found at {output_path}"
        )
