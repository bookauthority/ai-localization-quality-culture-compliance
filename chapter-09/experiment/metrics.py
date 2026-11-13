from typing import Dict, TypedDict


class RunRecord(TypedDict):
    variant: str
    workload_id: str
    run_id: str
    success: bool
    metrics: Dict[str, float]
