"""
Experiment Runner
BSM307 - Güz 2025

Her senaryo için 5 tekrar çalıştırır ve sonuçları toplar.
PDF gereksinimi: 5 tekrar (repetition) per scenario
"""

import time
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
import json

import networkx as nx

from src.algorithms.ga.genetic_algorithm import GeneticAlgorithm
from src.algorithms.aco.ant_colony import AntColonyOptimizer
from src.metrics.delay import total_delay
from src.metrics.reliability import reliability_cost
from src.metrics.resource_cost import bandwidth_cost
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ExperimentResult:
    """Tek bir experiment sonucu"""
    scenario_id: int
    repetition: int
    algorithm: str
    source: int
    target: int
    bandwidth: float
    path: List[int]
    path_length: int
    total_delay: float
    reliability_cost: float
    resource_cost: float
    weighted_cost: float
    runtime_seconds: float
    success: bool
    error_message: str = ""


class ExperimentRunner:
    """
    Her senaryo için algoritmaları çalıştırır ve sonuçları toplar.
    
    PDF gereksinimleri:
    - Her senaryo için 5 tekrar
    - GA ve ACO algoritmaları
    - Metrikler: delay, reliability, resource cost, weighted sum
    """
    
    def __init__(
        self,
        graph: nx.Graph,
        weights: Tuple[float, float, float] = (0.4, 0.3, 0.3),
        num_repetitions: int = 5
    ):
        """
        Args:
            graph: NetworkX graph objesi
            weights: (delay_weight, reliability_weight, resource_weight)
            num_repetitions: Her senaryo için tekrar sayısı (varsayılan: 5)
        """
        self.graph = graph
        self.weights = weights
        self.num_repetitions = num_repetitions
        
        logger.info(
            "Initialized ExperimentRunner: repetitions=%s, weights=%s",
            num_repetitions, weights
        )
    
    def run_single_experiment(
        self,
        scenario_id: int,
        source: int,
        target: int,
        bandwidth: float,
        algorithm: str,
        repetition: int,
        algorithm_seed: int = None
    ) -> ExperimentResult:
        """
        Tek bir experiment çalıştırır.
        
        Args:
            scenario_id: Senaryo ID
            source: Source node
            target: Target node
            bandwidth: Required bandwidth (Mbps)
            algorithm: "GA" veya "ACO"
            repetition: Tekrar numarası (0-4)
            algorithm_seed: Algoritma için seed (None = random)
            
        Returns:
            ExperimentResult objesi
        """
        start_time = time.time()
        result = ExperimentResult(
            scenario_id=scenario_id,
            repetition=repetition,
            algorithm=algorithm,
            source=source,
            target=target,
            bandwidth=bandwidth,
            path=[],
            path_length=0,
            total_delay=0.0,
            reliability_cost=0.0,
            resource_cost=0.0,
            weighted_cost=0.0,
            runtime_seconds=0.0,
            success=False
        )
        
        try:
            # Algoritma seed'i (her tekrar için farklı)
            if algorithm_seed is None:
                seed = scenario_id * 1000 + repetition * 100 + hash(algorithm) % 100
            else:
                seed = algorithm_seed + repetition
            
            # Algoritma çalıştır
            if algorithm == "GA":
                ga = GeneticAlgorithm(
                    graph=self.graph,
                    source=source,
                    target=target,
                    weights=self.weights,
                    required_bandwidth=bandwidth,
                    population_size=50,
                    crossover_rate=0.8,
                    mutation_rate=0.1,
                    seed=seed
                )
                path, cost = ga.run(generations=50)
                
            elif algorithm == "ACO":
                aco = AntColonyOptimizer(
                    graph=self.graph,
                    source=source,
                    target=target,
                    weights=self.weights,
                    required_bandwidth=bandwidth,
                    num_ants=30,
                    alpha=1.5,
                    beta=2.5,
                    evaporation_rate=0.15,
                    seed=seed
                )
                path, cost = aco.run(iterations=50)
                
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
            
            # Path kontrolü
            if not path or len(path) == 0:
                result.error_message = "No path found"
                result.runtime_seconds = time.time() - start_time
                return result
            
            # Metrikleri hesapla
            delay = total_delay(graph=self.graph, path=path)
            rel_cost = reliability_cost(graph=self.graph, path=path)
            res_cost = bandwidth_cost(graph=self.graph, path=path)
            
            # Sonuçları kaydet
            result.path = path
            result.path_length = len(path)
            result.total_delay = delay
            result.reliability_cost = rel_cost
            result.resource_cost = res_cost
            result.weighted_cost = cost
            result.runtime_seconds = time.time() - start_time
            result.success = True
            
            logger.debug(
                "Experiment success: scenario=%s, rep=%s, algo=%s, cost=%.4f, time=%.2fs",
                scenario_id, repetition, algorithm, cost, result.runtime_seconds
            )
            
        except Exception as e:
            result.error_message = str(e)
            result.runtime_seconds = time.time() - start_time
            logger.error(
                "Experiment failed: scenario=%s, rep=%s, algo=%s, error=%s",
                scenario_id, repetition, algorithm, str(e)
            )
        
        return result
    
    def run_scenario(
        self,
        scenario_id: int,
        source: int,
        target: int,
        bandwidth: float,
        algorithms: List[str] = ["GA", "ACO"]
    ) -> List[ExperimentResult]:
        """
        Bir senaryo için tüm tekrarları çalıştırır.
        
        Args:
            scenario_id: Senaryo ID
            source: Source node
            target: Target node
            bandwidth: Required bandwidth (Mbps)
            algorithms: Çalıştırılacak algoritmalar (varsayılan: ["GA", "ACO"])
            
        Returns:
            ExperimentResult listesi
        """
        results = []
        
        logger.info(
            "Running scenario %s: S=%s, D=%s, B=%.1f Mbps (%s repetitions, %s algorithms)",
            scenario_id, source, target, bandwidth, self.num_repetitions, len(algorithms)
        )
        
        for algorithm in algorithms:
            for repetition in range(self.num_repetitions):
                result = self.run_single_experiment(
                    scenario_id=scenario_id,
                    source=source,
                    target=target,
                    bandwidth=bandwidth,
                    algorithm=algorithm,
                    repetition=repetition
                )
                results.append(result)
                
                # Progress log
                if (repetition + 1) % 5 == 0 or repetition == self.num_repetitions - 1:
                    logger.info(
                        "  Progress: %s/%s repetitions completed for %s",
                        repetition + 1, self.num_repetitions, algorithm
                    )
        
        # Özet
        success_count = sum(1 for r in results if r.success)
        logger.info(
            "Scenario %s completed: %s/%s experiments successful",
            scenario_id, success_count, len(results)
        )
        
        return results
    
    def run_all_scenarios(
        self,
        scenarios: List[Tuple[int, int, float]],
        algorithms: List[str] = ["GA", "ACO"]
    ) -> List[ExperimentResult]:
        """
        Tüm senaryoları çalıştırır.
        
        Args:
            scenarios: (source, target, bandwidth) tuple'larının listesi
            algorithms: Çalıştırılacak algoritmalar
            
        Returns:
            Tüm experiment sonuçlarının listesi
        """
        all_results = []
        
        logger.info(
            "Starting experiment: %s scenarios, %s repetitions, %s algorithms",
            len(scenarios), self.num_repetitions, len(algorithms)
        )
        
        for scenario_id, (source, target, bandwidth) in enumerate(scenarios, 1):
            scenario_results = self.run_scenario(
                scenario_id=scenario_id,
                source=source,
                target=target,
                bandwidth=bandwidth,
                algorithms=algorithms
            )
            all_results.extend(scenario_results)
            
            logger.info(
                "Completed scenario %s/%s",
                scenario_id, len(scenarios)
            )
        
        logger.info(
            "Experiment completed: %s total results",
            len(all_results)
        )
        
        return all_results


def save_results_to_json(results: List[ExperimentResult], filepath: str) -> None:
    """
    Sonuçları JSON dosyasına kaydeder.
    
    Args:
        results: ExperimentResult listesi
        filepath: Kayıt dosyası yolu
    """
    data = [asdict(result) for result in results]
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info("Results saved to %s", filepath)


if __name__ == "__main__":
    # Test için
    from src.network.generator import RandomNetworkGenerator
    from experiments.scenario_generator import generate_scenarios_for_experiment
    
    print("=" * 60)
    print("BSM307 - Experiment Runner Test")
    print("=" * 60)
    
    # Graph oluştur
    gen = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    graph = gen.generate()
    graph = gen.attach_attributes(graph)
    
    print(f"\nGraph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    
    # Senaryoları üret (test için sadece 2 senaryo)
    scenarios = generate_scenarios_for_experiment(graph, num_scenarios=2, seed=42)
    
    # Experiment runner
    runner = ExperimentRunner(graph, num_repetitions=2)  # Test için 2 tekrar
    
    # Çalıştır
    results = runner.run_all_scenarios(scenarios, algorithms=["GA", "ACO"])
    
    print(f"\n✅ Experiment completed: {len(results)} results")
    for result in results[:5]:  # İlk 5 sonucu göster
        print(f"  Scenario {result.scenario_id}, Rep {result.repetition}, {result.algorithm}: "
              f"success={result.success}, cost={result.weighted_cost:.4f}, time={result.runtime_seconds:.2f}s")

