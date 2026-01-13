import subprocess
import time
from pathlib import Path

from config import PCEM_PATH

class PCemRunner:
    """
    Minimal PCem runner.
    Phase 1 responsibility:
      - launch PCem
      - keep it alive for observation window
      - return process handle
    """
    def launch(self, config_path: str):
        """
        Launch PCem with a given config file.
        """
        cmd = [
            PCEM_PATH,
            "-config",
            str(Path(config_path).resolve())
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return proc
