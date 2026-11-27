from __future__ import annotations

from collections.abc import Callable
from contextlib import redirect_stdout
from io import StringIO
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.generator.seed_source import seed
from src.iceberg_lab.catalog import get_catalog
from src.iceberg_lab.orders import ICEBERG_TABLE
from src.iceberg_lab.source import fetch_all_orders
from src.ingestion.initial_load import load_orders
from src.scenarios.corrupt_values import main as inject_corruption
from src.validation.profile import build_profile
from src.validation.quality_gate import (
    evaluate_profile,
    failed_results,
)

BASELINE_ROWS = 10_000

console = Console()


def quietly[T](
    function: Callable[..., T],
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Run an existing lab function while suppressing its
    developer-oriented terminal output.
    """
    output = StringIO()

    with redirect_stdout(output):
        return function(*args, **kwargs)


def current_profile() -> dict[str, Any]:
    catalog = get_catalog()
    table = catalog.load_table(ICEBERG_TABLE)

    return build_profile(table)


def prepare_healthy_baseline() -> dict[str, Any]:
    quietly(
        seed,
        BASELINE_ROWS,
    )

    source = fetch_all_orders()

    quietly(
        load_orders,
        source,
    )

    return current_profile()


def inject_and_commit_corruption() -> dict[str, Any]:
    quietly(inject_corruption)

    corrupted_source = fetch_all_orders()

    quietly(
        load_orders,
        corrupted_source,
    )

    return current_profile()


def metric(
    profile: dict[str, Any],
    column: str,
    metric_name: str,
) -> Any:
    return profile["metrics"][column][metric_name]


def print_title() -> None:
    console.print()

    console.print(
        Panel.fit(
            "[bold]Beyond Row Counts[/bold]\n"
            "Using Apache Iceberg Metadata "
            "for Reliable Data Pipelines",
            border_style="cyan",
        )
    )


def print_row_count_check(
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> None:
    baseline_count = baseline["record_count"]
    current_count = current["record_count"]

    passed = baseline_count == current_count

    table = Table(
        title="1. Traditional Row-Count Check",
        show_header=True,
    )

    table.add_column("Baseline", justify="right")
    table.add_column("Current", justify="right")
    table.add_column("Result", justify="center")

    table.add_row(
        f"{baseline_count:,}",
        f"{current_count:,}",
        ("[green]PASS[/green]" if passed else "[red]FAIL[/red]"),
    )

    console.print()
    console.print(table)

    if passed:
        console.print("\n[green]✓[/green] Everything looks healthy if we only check row counts.")


def print_metadata_check(
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> int:
    results = evaluate_profile(current)

    by_rule = {(result.column, result.rule): result for result in results}

    checks = [
        (
            "quantity upper bound",
            metric(
                baseline,
                "quantity",
                "upper_bound",
            ),
            metric(
                current,
                "quantity",
                "upper_bound",
            ),
            by_rule[("quantity", "max_value")],
        ),
        (
            "total_amount upper bound",
            metric(
                baseline,
                "total_amount",
                "upper_bound",
            ),
            metric(
                current,
                "total_amount",
                "upper_bound",
            ),
            by_rule[("total_amount", "max_value")],
        ),
        (
            "state recorded upper bound",
            metric(
                baseline,
                "state",
                "upper_bound",
            ),
            metric(
                current,
                "state",
                "upper_bound",
            ),
            by_rule[
                (
                    "state",
                    "allowed_upper_bound",
                )
            ],
        ),
        (
            "quantity null count",
            metric(
                baseline,
                "quantity",
                "null_count",
            ),
            metric(
                current,
                "quantity",
                "null_count",
            ),
            by_rule[("quantity", "null_count")],
        ),
        (
            "total_amount null count",
            metric(
                baseline,
                "total_amount",
                "null_count",
            ),
            metric(
                current,
                "total_amount",
                "null_count",
            ),
            by_rule[
                (
                    "total_amount",
                    "null_count",
                )
            ],
        ),
    ]

    table = Table(
        title="2. Iceberg Metadata Quality Gate",
        show_header=True,
    )

    table.add_column("Metadata Signal")
    table.add_column(
        "Baseline",
        justify="right",
    )
    table.add_column(
        "Current",
        justify="right",
    )
    table.add_column("Expected")
    table.add_column(
        "Result",
        justify="center",
    )

    for (
        label,
        baseline_value,
        current_value,
        result,
    ) in checks:
        status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"

        table.add_row(
            label,
            str(baseline_value),
            str(current_value),
            str(result.expected),
            status,
        )

    console.print()
    console.print(table)

    failures = failed_results(results)

    return len(failures)


def print_snapshots(
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> None:
    console.print(
        f"\n[dim]Iceberg snapshot {baseline['snapshot_id']} → {current['snapshot_id']}[/dim]"
    )


def print_takeaway(
    failure_count: int,
) -> None:
    console.print()

    console.print(
        Panel.fit(
            "[bold green]"
            "ROW COUNT: PASS"
            "[/bold green]\n"
            "[bold red]"
            "METADATA QUALITY GATE: "
            f"FAIL ({failure_count} violations)"
            "[/bold red]\n\n"
            "Same row count. Different data quality.",
            title="Takeaway",
            border_style="yellow",
        )
    )

    console.print(
        "\n[dim]"
        "Iceberg metadata provides inexpensive reliability signals — "
        "it does not replace full data-quality testing."
        "[/dim]"
    )

    console.print(
        "[dim]"
        "Demo note: the state check uses Iceberg's recorded "
        "lexicographic upper bound, not full domain validation."
        "[/dim]"
    )


def main() -> None:
    print_title()

    console.print("\n[dim]Preparing deterministic healthy baseline...[/dim]")

    baseline = prepare_healthy_baseline()

    console.print("[green]✓[/green] Healthy 10,000-row Iceberg baseline ready.")

    console.print(
        "\n[dim]Injecting controlled data corruption without changing the row count...[/dim]"
    )

    current = inject_and_commit_corruption()

    console.print("[yellow]✓[/yellow] Corrupted data committed as a new Iceberg snapshot.")

    print_row_count_check(
        baseline,
        current,
    )

    failures = print_metadata_check(
        baseline,
        current,
    )

    print_snapshots(
        baseline,
        current,
    )

    print_takeaway(failures)


if __name__ == "__main__":
    main()
