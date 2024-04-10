from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Iterable, Protocol, Tuple, Type


class BenchmarkCatalog:
    def __init__(self) -> None:
        self.registered_benchmark_classes: Dict[str, Type[Benchmark]] = dict()

    def register_benchmark(self, name: str, benchmark_class: Type[Benchmark]) -> None:
        self.registered_benchmark_classes[name] = benchmark_class

    def get_all_benchmarks(self) -> Iterable[Tuple[str, Type[Benchmark]]]:
        for name, benchmark_class in self.registered_benchmark_classes.items():
            yield name, benchmark_class


class Benchmark(Protocol):
    def __init__(self) -> None: ...

    def tear_down(self) -> None: ...

    def run(self) -> None: ...


@dataclass
class BenchmarkResult:
    name: str
    average_execution_time_in_secs: float


def render_results_as_json(results: Dict[str, BenchmarkResult]) -> str:
    def result_to_json(result: BenchmarkResult):
        return {
            "name": result.name,
            "average_execution_time_in_secs": result.average_execution_time_in_secs,
        }

    report_json = {name: result_to_json(result) for name, result in results.items()}
    return json.dumps(report_json, indent=4)
