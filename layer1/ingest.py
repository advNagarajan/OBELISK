import os
from layer1.models import ArtifactDescriptor, FileEntry
from layer1.detect import detect_file_type, detect_bootable
from layer1.hashutil import sha256_file
from layer1.walk import walk_directory
from layer1.normalize import (
    artifact_id_from_path,
    create_artifact_dir,
    normalize_single_file,
    normalize_directory,
    normalize_zip
)

def ingest(path: str) -> ArtifactDescriptor:
    has_init = False
    artifact_id = artifact_id_from_path(path)
    artifact_dir = create_artifact_dir(artifact_id)

    original_name = os.path.basename(path)
    files = []
    file_types = set()
    container = False
    disk_image = False
    bootable = False
    inner_disk_image = False
    inner_bootable = False

    KNOWN_FLOPPY_SIZES = {
        163840,    # 160 KB
        184320,    # 180 KB
        327680,    # 320 KB
        368640,    # 360 KB
        737280,    # 720 KB
        1228800,   # 1.2 MB
        1474560,   # 1.44 MB
    }

    if os.path.isfile(path):
        ftype = detect_file_type(path)
        size = os.path.getsize(path)

        is_raw_floppy = (
            ftype == "boot_sector" and
            size in KNOWN_FLOPPY_SIZES
        )

        if ftype == "zip":
            source_type = "archive"
            container = True
            normalize_zip(path, artifact_dir)

        elif ftype == "disk_image" or is_raw_floppy:
            source_type = "disk_image"
            disk_image = True
            bootable = detect_bootable(path)
            normalize_single_file(path, artifact_dir)

        else:
            source_type = "single_file"
            normalize_single_file(path, artifact_dir)

    elif os.path.isdir(path):
        source_type = "directory"
        container = True
        normalize_directory(path, artifact_dir)

    else:
        raise ValueError("Unsupported input")

    for full, rel in walk_directory(artifact_dir):
        ftype = detect_file_type(full)
        size = os.path.getsize(full)
        file_types.add(ftype)

        st = os.stat(full)
        mode = st.st_mode

        if rel == "init":
            has_init = True

        if ftype in ("disk_image", "boot_sector"):
            inner_disk_image = True
            if detect_bootable(full):
                inner_bootable = True

        files.append(
            FileEntry(
                path=rel,
                size=size,
                hash=sha256_file(full),
                mode=mode        # ✅ NEW
            )
        )

    if container:
        disk_image = inner_disk_image
        bootable = inner_bootable

    # 🔹 NEW: execution surface inference (Layer-1 safe)
    execution_surfaces = []

    if bootable:
        execution_surfaces.append("boot_disk")

    if "exe" in file_types or "com" in file_types:
        execution_surfaces.append("dos_executable")

    if "elf" in file_types:
        execution_surfaces.append("linux_elf")

    if "script" in file_types:
        execution_surfaces.append("linux_script")

    if has_init:
        execution_surfaces.append("linux_init")

    if not execution_surfaces:
        execution_surfaces.append("non_executable")

    return ArtifactDescriptor(
        artifact_id=artifact_id,
        source_type=source_type,
        original_name=original_name,
        normalized_path=artifact_dir,
        files=files,
        file_types=sorted(file_types),
        container=container,
        disk_image=disk_image,
        bootable=bootable,
        execution_surfaces=execution_surfaces,
        has_init=has_init
    )
