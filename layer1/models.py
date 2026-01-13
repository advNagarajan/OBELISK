from dataclasses import dataclass
from typing import List

@dataclass
class FileEntry:
    path: str            # relative to artifact root
    size: int
    hash: str

@dataclass
class ArtifactDescriptor:
    artifact_id: str
    source_type: str     # single_file | directory | archive | disk_image
    original_name: str
    normalized_path: str
    files: List[FileEntry]
    file_types: List[str]
    container: bool
    disk_image: bool
    bootable:bool 
    execution_surfaces: List[str]