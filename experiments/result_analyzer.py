"""
Result Analyzer
BSM307 - Güz 2025

Experiment sonuçlarını analiz eder ve özetler.
"""

import json
import statistics
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass

from experiments.experiment_runner import ExperimentResult
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ScenarioSummary:
    """Bir senaryo için özet istatistikler"""
    scenario_id: int
    source: int
    target: int
    bandwidth: float
    algorithm: str
    
    # Başarı oranı
    success_count: int
    total_count: int
    success_rate: float
    
    # Metrikler (ortalama ± std)
    avg_path_length: float
    std_path_length: float
    
    avg_delay: float
    std_delay: float
    
    avg_reliability_cost: float
    std_reliability_cost: float
    
    avg_resource_cost: float
    std_resource_cost: float
    
    avg_weighted_cost: float
    std_weighted_cost: float
    
    avg_runtime: float
    std_runtime: float


class ResultAnalyzer:
    """
    Experiment sonuçlarını analiz eder.
    
    PDF gereksinimleri:
    - Ortalama ve standart sapma hesaplama
    - Algoritma karşılaştırması
    - Senaryo bazlı analiz
    """
    
    def __init__(self, results: List[ExperimentResult]):
        """
        Args:
            results: ExperimentResult listesi
        """
        self.results = results
        logger.info("Initialized ResultAnalyzer with %s results", len(results))
    
    def group_by_scenario_and_algorithm(self) -> Dict[Tuple[int, str], List[ExperimentResult]]:
        """
        Sonuçları senaryo ve algoritma bazında gruplar.
        
        Returns:
            {(scenario_id, algorithm): [results]} dictionary
        """
        grouped = defaultdict(list)
        
        for result in self.results:
            key = (result.scenario_id, result.algorithm)
            grouped[key].append(result)
        
        return dict(grouped)
    
    def calculate_summary(self, results: List[ExperimentResult]) -> ScenarioSummary:
        """
        Bir grup sonuç için özet istatistikler hesaplar.
        
        Args:
            results: Aynı senaryo ve algoritma için sonuçlar
            
        Returns:
            ScenarioSummary objesi
        """
        if not results:
            raise ValueError("Empty results list")
        
        first_result = results[0]
        
        # Başarı oranı
        success_results = [r for r in results if r.success]
        success_count = len(success_results)
        total_count = len(results)
        success_rate = success_count / total_count if total_count > 0 else 0.0
        
        if not success_results:
            # Başarılı sonuç yok, default değerler
            return ScenarioSummary(
                scenario_id=first_result.scenario_id,
                source=first_result.source,
                target=first_result.target,
                bandwidth=first_result.bandwidth,
                algorithm=first_result.algorithm,
                success_count=0,
                total_count=total_count,
                success_rate=0.0,
                avg_path_length=0.0,
                std_path_length=0.0,
                avg_delay=0.0,
                std_delay=0.0,
                avg_reliability_cost=0.0,
                std_reliability_cost=0.0,
                avg_resource_cost=0.0,
                std_resource_cost=0.0,
                avg_weighted_cost=0.0,
                std_weighted_cost=0.0,
                avg_runtime=0.0,
                std_runtime=0.0
            )
        
        # Metrikler
        path_lengths = [r.path_length for r in success_results]
        delays = [r.total_delay for r in success_results]
        rel_costs = [r.reliability_cost for r in success_results]
        res_costs = [r.resource_cost for r in success_results]
        weighted_costs = [r.weighted_cost for r in success_results]
        runtimes = [r.runtime_seconds for r in success_results]
        
        def mean_std(values: List[float]) -> tuple:
            if len(values) == 0:
                return 0.0, 0.0
            elif len(values) == 1:
                return values[0], 0.0
            else:
                return statistics.mean(values), statistics.stdev(values)
        
        avg_path_length, std_path_length = mean_std(path_lengths)
        avg_delay, std_delay = mean_std(delays)
        avg_rel_cost, std_rel_cost = mean_std(rel_costs)
        avg_res_cost, std_res_cost = mean_std(res_costs)
        avg_weighted_cost, std_weighted_cost = mean_std(weighted_costs)
        avg_runtime, std_runtime = mean_std(runtimes)
        
        return ScenarioSummary(
            scenario_id=first_result.scenario_id,
            source=first_result.source,
            target=first_result.target,
            bandwidth=first_result.bandwidth,
            algorithm=first_result.algorithm,
            success_count=success_count,
            total_count=total_count,
            success_rate=success_rate,
            avg_path_length=avg_path_length,
            std_path_length=std_path_length,
            avg_delay=avg_delay,
            std_delay=std_delay,
            avg_reliability_cost=avg_rel_cost,
            std_reliability_cost=std_rel_cost,
            avg_resource_cost=avg_res_cost,
            std_resource_cost=std_res_cost,
            avg_weighted_cost=avg_weighted_cost,
            std_weighted_cost=std_weighted_cost,
            avg_runtime=avg_runtime,
            std_runtime=std_runtime
        )
    
    def generate_summaries(self) -> List[ScenarioSummary]:
        """
        Tüm senaryolar için özet istatistikler üretir.
        
        Returns:
            ScenarioSummary listesi
        """
        grouped = self.group_by_scenario_and_algorithm()
        summaries = []
        
        for (scenario_id, algorithm), results in sorted(grouped.items()):
            summary = self.calculate_summary(results)
            summaries.append(summary)
        
        logger.info("Generated %s summaries", len(summaries))
        return summaries
    
    def compare_algorithms(self) -> Dict[str, Dict[str, float]]:
        """
        Algoritmaları karşılaştırır.
        
        Returns:
            Algoritma bazında ortalama metrikler
        """
        summaries = self.generate_summaries()
        
        algo_stats = defaultdict(lambda: {
            'total_scenarios': 0,
            'success_rate': [],
            'avg_cost': [],
            'avg_delay': [],
            'avg_runtime': []
        })
        
        for summary in summaries:
            algo = summary.algorithm
            algo_stats[algo]['total_scenarios'] += 1
            algo_stats[algo]['success_rate'].append(summary.success_rate)
            if summary.avg_weighted_cost > 0:
                algo_stats[algo]['avg_cost'].append(summary.avg_weighted_cost)
            if summary.avg_delay > 0:
                algo_stats[algo]['avg_delay'].append(summary.avg_delay)
            if summary.avg_runtime > 0:
                algo_stats[algo]['avg_runtime'].append(summary.avg_runtime)
        
        comparison = {}
        for algo, stats in algo_stats.items():
            comparison[algo] = {
                'total_scenarios': stats['total_scenarios'],
                'avg_success_rate': statistics.mean(stats['success_rate']) if stats['success_rate'] else 0.0,
                'avg_cost': statistics.mean(stats['avg_cost']) if stats['avg_cost'] else 0.0,
                'avg_delay': statistics.mean(stats['avg_delay']) if stats['avg_delay'] else 0.0,
                'avg_runtime': statistics.mean(stats['avg_runtime']) if stats['avg_runtime'] else 0.0
            }
        
        return comparison
    
    def export_to_csv(self, filepath: str) -> None:
        """
        Özetleri CSV dosyasına export eder.
        
        Args:
            filepath: CSV dosyası yolu
        """
        summaries = self.generate_summaries()
        
        import csv
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Scenario_ID', 'Source', 'Target', 'Bandwidth', 'Algorithm',
                'Success_Rate', 'Success_Count', 'Total_Count',
                'Avg_Path_Length', 'Std_Path_Length',
                'Avg_Delay', 'Std_Delay',
                'Avg_Reliability_Cost', 'Std_Reliability_Cost',
                'Avg_Resource_Cost', 'Std_Resource_Cost',
                'Avg_Weighted_Cost', 'Std_Weighted_Cost',
                'Avg_Runtime', 'Std_Runtime'
            ])
            
            # Data
            for summary in summaries:
                writer.writerow([
                    summary.scenario_id,
                    summary.source,
                    summary.target,
                    summary.bandwidth,
                    summary.algorithm,
                    f"{summary.success_rate:.4f}",
                    summary.success_count,
                    summary.total_count,
                    f"{summary.avg_path_length:.2f}",
                    f"{summary.std_path_length:.2f}",
                    f"{summary.avg_delay:.4f}",
                    f"{summary.std_delay:.4f}",
                    f"{summary.avg_reliability_cost:.4f}",
                    f"{summary.std_reliability_cost:.4f}",
                    f"{summary.avg_resource_cost:.4f}",
                    f"{summary.std_resource_cost:.4f}",
                    f"{summary.avg_weighted_cost:.4f}",
                    f"{summary.std_weighted_cost:.4f}",
                    f"{summary.avg_runtime:.2f}",
                    f"{summary.std_runtime:.2f}"
                ])
        
        logger.info("Summaries exported to CSV: %s", filepath)
    
    def print_summary_report(self) -> None:
        """
        Konsola özet rapor yazdırır.
        """
        summaries = self.generate_summaries()
        comparison = self.compare_algorithms()
        
        print("\n" + "=" * 80)
        print("BSM307 - Experiment Results Summary")
        print("=" * 80)
        
        print(f"\nTotal Results: {len(self.results)}")
        print(f"Total Summaries: {len(summaries)}")
        
        # Algoritma karşılaştırması
        print("\n" + "-" * 80)
        print("Algorithm Comparison")
        print("-" * 80)
        for algo, stats in comparison.items():
            print(f"\n{algo}:")
            print(f"  Scenarios: {stats['total_scenarios']}")
            print(f"  Avg Success Rate: {stats['avg_success_rate']:.4f}")
            print(f"  Avg Weighted Cost: {stats['avg_cost']:.4f}")
            print(f"  Avg Delay: {stats['avg_delay']:.4f}")
            print(f"  Avg Runtime: {stats['avg_runtime']:.2f}s")
        
        # Senaryo özetleri (ilk 5)
        print("\n" + "-" * 80)
        print("Scenario Summaries (first 5)")
        print("-" * 80)
        for summary in summaries[:5]:
            print(f"\nScenario {summary.scenario_id} ({summary.algorithm}):")
            print(f"  S={summary.source}, D={summary.target}, B={summary.bandwidth:.1f} Mbps")
            print(f"  Success: {summary.success_count}/{summary.total_count} ({summary.success_rate:.2%})")
            print(f"  Cost: {summary.avg_weighted_cost:.4f} ± {summary.std_weighted_cost:.4f}")
            print(f"  Delay: {summary.avg_delay:.4f} ± {summary.std_delay:.4f}")
            print(f"  Runtime: {summary.avg_runtime:.2f}s ± {summary.std_runtime:.2f}s")


def load_results_from_json(filepath: str) -> List[ExperimentResult]:
    """
    JSON dosyasından sonuçları yükler.
    
    Args:
        filepath: JSON dosyası yolu
        
    Returns:
        ExperimentResult listesi
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    results = []
    for item in data:
        result = ExperimentResult(**item)
        results.append(result)
    
    logger.info("Loaded %s results from %s", len(results), filepath)
    return results


if __name__ == "__main__":
    # Test için
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python result_analyzer.py <results.json>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    results = load_results_from_json(filepath)
    
    analyzer = ResultAnalyzer(results)
    analyzer.print_summary_report()
    
    # CSV export
    csv_path = filepath.replace('.json', '_summary.csv')
    analyzer.export_to_csv(csv_path)
    print(f"\n✅ Summary exported to: {csv_path}")

