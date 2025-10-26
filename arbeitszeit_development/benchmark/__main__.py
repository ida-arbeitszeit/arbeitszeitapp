from __future__ import annotations

import argparse
import timeit
from dataclasses import dataclass
from typing import Dict, Optional, Self

from .get_company_summary_benchmark import GetCompanySummaryBenchmark
from .get_statistics import GetStatisticsBenchmark
from .query_plans_sorted_by_activation_date_benchmark import (
    QueryPlansSortedByActivationDateBenchmark,
)
from .runner import BenchmarkCatalog, BenchmarkResult, render_results_as_json
from .show_prd_account_details_benchmark import ShowPrdAccountDetailsBenchmark
from .show_r_account_details_benchmark import ShowRAccountDetailsBenchmark


def build_benchmark_catalog() -> BenchmarkCatalog:
    catalog = BenchmarkCatalog()
    catalog.register_benchmark(
        "show_prd_account_details", ShowPrdAccountDetailsBenchmark
    )
    catalog.register_benchmark("show_r_account_details", ShowRAccountDetailsBenchmark)
    catalog.register_benchmark("get_statistics", GetStatisticsBenchmark)
    catalog.register_benchmark("get_company_summary", GetCompanySummaryBenchmark)
    catalog.register_benchmark(
        "query_plans_sorted_by_activation_date",
        QueryPlansSortedByActivationDateBenchmark,
    )
    return catalog


def main() -> None:
    arguments = parse_arguments()
    configuration = Configuration.from_arguments(arguments)
    results: Dict[str, BenchmarkResult] = dict()
    catalog = build_benchmark_catalog()
    for name, benchmark_class in catalog.get_all_benchmarks():
        if (configuration.include_filter or "") not in name:
            continue
        print(f"Running benchmark: {name}")
        benchmark = benchmark_class()
        try:
            average_benchmark_time = (
                timeit.timeit(benchmark.run, number=configuration.repeats)
                / configuration.repeats
            )
        finally:
            benchmark.tear_down()
        results[name] = BenchmarkResult(
            name=name, average_execution_time_in_secs=average_benchmark_time
        )
    print(render_results_as_json(results))


@dataclass
class Configuration:
    repeats: int
    include_filter: Optional[str]

    @classmethod
    def from_arguments(cls, arguments: argparse.Namespace) -> Self:
        return cls(
            repeats=arguments.repeats,
            include_filter=arguments.include,
        )


def parse_arguments() -> argparse.Namespace:
    catalog = build_benchmark_catalog()
    available_benchmarks = ", ".join(name for name, _ in catalog.get_all_benchmarks())
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--include",
        "-i",
        default=None,
        help=f"Filter benchmarks by name substring. Available: {available_benchmarks}",
    )
    parser.add_argument(
        "--repeats",
        "-n",
        type=int,
        default=5,
        help="Number of times to repeat each benchmark",
    )
    return parser.parse_args()


main()
