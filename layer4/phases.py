PHASES = [
    "emulator_started",
    "filesystem_mounted",
    "entrypoint_invoked",
    "control_transferred",
    "stability_window_reached"
]
# NOTE:
# PHASES are interpreted differently depending on execution_mode:
# - PROCESS mode (DOS, DOS-QEMU): phases reflect program lifecycle
# - SYSTEM mode (Linux): phases reflect system boot stability