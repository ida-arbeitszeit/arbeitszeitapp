from __future__ import annotations

import timeit
from typing import Dict

from .get_company_transactions import GetCompanyTransactionsBenchmark
from .runner import BenchmarkCatalog, BenchmarkResult, render_results_as_json
from .show_prd_account_details_benchmark import ShowPrdAccountDetailsBenchmark


def main() -> None:
    repeats = 5
    results: Dict[str, BenchmarkResult] = dict()
    catalog = BenchmarkCatalog()
    catalog.register_benchmark(
        name="get_company_transactions", benchmark_class=GetCompanyTransactionsBenchmark
    )
    catalog.register_benchmark(
        name="show_prd_account_details", benchmark_class=ShowPrdAccountDetailsBenchmark
    )
    for name, benchmark in catalog.get_all_benchmarks():
        try:
            average_benchmark_time = (
                timeit.timeit(benchmark.run, number=repeats) / repeats
            )
        finally:
            benchmark.tear_down()
        results[name] = BenchmarkResult(
            name=name, average_execution_time_in_secs=average_benchmark_time
        )
    print(render_results_as_json(results))


main()
