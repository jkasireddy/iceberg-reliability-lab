from __future__ import annotations

from dataclasses import dataclass
from typing import Any

WATCHED_METRICS = {
    "quantity": (
        "null_count",
        "lower_bound",
        "upper_bound",
    ),
    "total_amount": (
        "null_count",
        "lower_bound",
        "upper_bound",
    ),
    "state": (
        "null_count",
        "lower_bound",
        "upper_bound",
    ),
    "updated_at": (
        "null_count",
        "lower_bound",
        "upper_bound",
    ),
}


@dataclass(frozen=True)
class MetricChange:
    column: str
    metric: str
    baseline: Any
    current: Any

    @property
    def changed(self) -> bool:
        return self.baseline != self.current


@dataclass(frozen=True)
class ProfileComparison:
    baseline_snapshot_id: int
    current_snapshot_id: int
    baseline_record_count: int
    current_record_count: int
    metric_changes: tuple[MetricChange, ...]

    @property
    def row_count_matches(self) -> bool:
        return self.baseline_record_count == self.current_record_count

    @property
    def changed_metrics(
        self,
    ) -> tuple[MetricChange, ...]:
        return tuple(change for change in self.metric_changes if change.changed)

    @property
    def has_metadata_drift(self) -> bool:
        return bool(self.changed_metrics)


def compare_profiles(
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> ProfileComparison:
    metric_changes: list[MetricChange] = []

    for column, metric_names in WATCHED_METRICS.items():
        for metric_name in metric_names:
            metric_changes.append(
                MetricChange(
                    column=column,
                    metric=metric_name,
                    baseline=baseline["metrics"][column][metric_name],
                    current=current["metrics"][column][metric_name],
                )
            )

    return ProfileComparison(
        baseline_snapshot_id=int(baseline["snapshot_id"]),
        current_snapshot_id=int(current["snapshot_id"]),
        baseline_record_count=int(baseline["record_count"]),
        current_record_count=int(current["record_count"]),
        metric_changes=tuple(metric_changes),
    )
