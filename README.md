# OBELISK

**OBELISK** (Omnibus Bootable Emulation Layer for Inferred System Kernels)  
A framework for studying execution compatibility across reconstructed software environments.

---

## Overview

OBELISK is a layered research framework designed to model and evaluate execution compatibility of software artifacts across reconstructed runtime environments.

Traditional software maintenance and evolution research often assumes executability. OBELISK makes execution compatibility explicit by systematically reconstructing compatible environments and observing execution outcomes.

The framework supports heterogeneous execution targets including:

- DOS-based systems (DOSBox, QEMU + FreeDOS)
- Dynamically generated Alpine Linux images
- Zephyr-based real-time operating systems (RTOS) via QEMU

OBELISK is designed for controlled, repeatable experimentation.

---

## Architecture

OBELISK follows a five-layer architecture:

1. **Artifact Ingestion**  
   Normalizes and prepares the input artifact.

2. **System Profiling**  
   Derives an artifact-specific system profile to determine environment requirements.

3. **Configuration Generation**  
   Produces compatible emulator configurations based on the derived profile.

4. **Execution Orchestration**  
   Launches and controls execution within reconstructed environments.

5. **Output Synthesis**  
   Collects structured execution outcomes for compatibility analysis.

The environment reconstruction process is deterministic and artifact-guided.

---

## Supported Execution Environments

### DOS
- DOSBox execution
- QEMU + FreeDOS using automated `fdauto.bat` injection

### Linux
- Runtime generation of minimal Alpine Linux images
- Artifact invocation within controlled boot environments

### RTOS
- Zephyr-based reconstruction
- QEMU-based RTOS execution

---

## Installation

### Prerequisites

- Python 3.10+
- QEMU (recommended latest stable)
- DOSBox
- Zephyr SDK (for RTOS support)
- Alpine Linux base image tools

Ensure all required toolchains are installed and accessible in your system PATH.

---
