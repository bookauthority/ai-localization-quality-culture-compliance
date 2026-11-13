import json
import sys
from typing import Any, Dict


def log_json(event: str, **kwargs: Any) -> None:
    record: Dict[str, Any] = {"event": event}
    record.update(kwargs)
    json.dump(record, sys.stdout)
    sys.stdout.write("\n")
    sys.stdout.flush()
