from __future__ import annotations

import contextlib
import json
import sys
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, Iterator, Optional


@dataclass
class MetricRecorder:
    """Collects numeric metrics for a single run.

    All metrics must be finite numbers; other values are not permitted.
    MetricRecorder is the single source of truth for validating metric
    values before they are written into evidence.
    """

    metrics: Dict[str, float] = field(default_factory=dict)

    def record(self, name: str, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError(f"Metric '{name}' must be numeric; got {type(value)!r}")
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError(f"Metric '{name}' must be finite; got {value!r}")
        self.metrics[name] = float(value)


class StructuredLogger:
    """Very small JSON logger.

    In a real system this would emit to a centralized log sink; here we
    write compact JSON to stdout to demonstrate the instrumentation
    structure. Log entries contain nondeterministic timestamps, but
    these logs are never read back into the experiment evidence, so
    they cannot affect the determinism of results.json.
    """

    def __init__(self, correlation_id: Optional[str] = None) -> None:
        self.correlation_id = correlation_id or str(uuid.uuid4())

    def _log(self, level: str, message: str, **fields: Any) -> None:
        payload = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            "correlation_id": self.correlation_id,
        }
        payload.update(fields)
        sys.stdout.write(json.dumps(payload) + "\n")

    def info(self, message: str, **fields: Any) -> None:
        self._log("INFO", message, **fields)

    def warning(self, message: str, **fields: Any) -> None:
        self._log("WARNING", message, **fields)

    def error(self, message: str, **fields: Any) -> None:
        self._log("ERROR", message, **fields)


class StageTimer:
    """Context manager to time a pipeline stage and log it.

    This implementation intentionally avoids using wall-clock timing for
    metrics to keep the experiment fully deterministic across runs.
    """

    def __init__(
        self,
        logger: StructuredLogger,
        recorder: MetricRecorder,
        stage_name: str,
        simulated_latency_ms: float,
    ) -> None:
        self.logger = logger
        self.recorder = recorder
        self.stage_name = stage_name
        self.simulated_latency_ms = simulated_latency_ms

    def __enter__(self) -> "StageTimer":
        # We still log a real timestamp for observability demonstration,
        # but it is not used for any metric values.
        self.logger.info("stage_start", stage=self.stage_name)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        metric_name = f"stage_{self.stage_name}_latency_ms"
        self.recorder.record(metric_name, self.simulated_latency_ms)
        self.logger.info(
            "stage_end",
            stage=self.stage_name,
            latency_ms=self.simulated_latency_ms,
        )


@contextlib.contextmanager
def timed_stage(
    logger: StructuredLogger,
    recorder: MetricRecorder,
    stage_name: str,
    simulated_latency_ms: float,
):
    """Context manager wrapper for a deterministically timed pipeline stage.

    Usage::

        with timed_stage(logger, recorder, "ingestion", 12.3):
            do_work()
    """

    timer = StageTimer(logger, recorder, stage_name, simulated_latency_ms)
    try:
        timer.__enter__()
        yield timer
    finally:
        timer.__exit__(None, None, None)
