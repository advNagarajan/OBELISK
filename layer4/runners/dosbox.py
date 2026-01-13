import subprocess
from pathlib import Path
from config import DOSBOX_PATH

class DOSBoxRunner:
    def launch(self, plan):
        LOG_DIR = Path("layer4_output/logs")
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        log_path = LOG_DIR / f"{plan.variant}_dosbox.log"

        proc = subprocess.Popen(
            [
                DOSBOX_PATH,
                "-conf", plan.config_path,
                "-logfile", str(log_path)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return proc, log_path
