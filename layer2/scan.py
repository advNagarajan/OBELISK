import os


def global_scan(artifact):
    signals = {
        "exe": 0,
        "com": 0,
        "bat": 0,
        "dll": 0,
        "pyd": 0,
        "boot": 0,
        "zephyr_prj": 0,
        "cmake": 0,
        "kconfig": 0,
        "west_manifest": 0,

        "zephyr_source": 0
    }

    for f in artifact.files:
        name = f.path.lower()
        if name.endswith(".exe"):
            signals["exe"] += 1
        elif name.endswith(".com"):
            signals["com"] += 1
        elif name.endswith(".bat"):
            signals["bat"] += 1
        elif name.endswith(".dll"):
            signals["dll"] += 1
        elif name.endswith(".pyd"):
            signals["pyd"] += 1
            
        # --- NEW: Zephyr project detection ---
        if name.endswith("prj.conf"):
            signals["zephyr_prj"] += 1

        elif name.endswith("cmakelists.txt"):
            signals["cmake"] += 1

        elif name.endswith("kconfig"):
            signals["kconfig"] += 1

        elif name.endswith("west.yml"):
            signals["west_manifest"] += 1

        if name.endswith(".c"):
            try:
                with open(os.path.join(artifact.normalized_path, f.path), "r", errors="ignore") as src:
                    text = src.read().lower()

                    if "zephyr/" in text or "printk(" in text or "k_thread" in text:
                        signals["zephyr_source"] += 1

            except Exception:
                pass

    return signals
