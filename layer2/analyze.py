from layer2.scan import global_scan
from layer2.candidates import find_entry_points
from layer2.inspect import inspect_candidates
from layer2.infer import infer_requirements
from layer2.synthesize import synthesize
from layer1.models import ArtifactDescriptor

def analyze(artifact: ArtifactDescriptor):
    scan = global_scan(artifact)
    candidates = find_entry_points(artifact)
    inspection = inspect_candidates(artifact, candidates)
    inference = infer_requirements(scan, inspection, artifact)
    return synthesize(artifact, scan, candidates, inspection, inference)
