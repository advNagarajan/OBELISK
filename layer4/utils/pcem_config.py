from pathlib import Path

def write_minimal_pcem_config(cfg_path: str, disk_image: str):
    """
    Writes a single conservative PCem config.
    This is Phase 1 only.
    """

    cfg = Path(cfg_path)
    cfg.parent.mkdir(parents=True, exist_ok=True)

    with cfg.open("w") as f:
        f.write("[machine]\n")
        f.write("cpu=386\n")
        f.write("mem=32\n")
        f.write("machine=ibm386\n\n")

        f.write("[video]\n")
        f.write("adapter=vga\n\n")

        f.write("[sound]\n")
        f.write("enabled=0\n\n")

        f.write("[storage]\n")
        f.write(f"floppy0={disk_image}\n")