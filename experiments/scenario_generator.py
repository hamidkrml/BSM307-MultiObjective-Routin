"""
Senaryo Üretici
BSM307 - Güz 2025

20 farklı (S, D, B) senaryosu üretir.
PDF gereksinimi: 20 farklı S-D-B kombinasyonu
"""

import random
from typing import List, Tuple

from src.network.generator import RandomNetworkGenerator
from src.utils.logger import get_logger
import networkx as nx

logger = get_logger(__name__)


class ScenarioGenerator:
    """
    20 farklı (Source, Destination, Bandwidth) senaryosu üretir.
    
    PDF gereksinimleri:
    - 20 farklı (S, D, B) kombinasyonu
    - S, D: 0-249 arası düğümler (path olmalı)
    - B: 100-1000 Mbps arası bandwidth
    """
    
    def __init__(self, graph: nx.Graph, num_scenarios: int = 20, seed: int = 42):
        """
        Args:
            graph: NetworkX graph objesi
            num_scenarios: Üretilecek senaryo sayısı (varsayılan: 20)
            seed: Rastgele tohum
        """
        self.graph = graph
        self.num_scenarios = num_scenarios
        self.seed = seed
        
        if seed is not None:
            random.seed(seed)
        
        logger.info(
            "Initialized ScenarioGenerator: num_scenarios=%s, seed=%s",
            num_scenarios, seed
        )
    
    def generate_scenarios(self) -> List[Tuple[int, int, float]]:
        """
        20 farklı (S, D, B) senaryosu üretir.
        
        Strateji:
        1. Graph'ten rastgele S-D çiftleri seç (path olmalı)
        2. Bandwidth değerleri: 100-1000 Mbps arası (PDF gereksinimi)
        3. Farklı kombinasyonlar sağla
        
        Returns:
            (source, target, bandwidth) tuple'larının listesi
        """
        scenarios = []
        nodes = list(self.graph.nodes())
        max_node = max(nodes)
        
        # Bandwidth aralığı (PDF: 100-1000 Mbps)
        bandwidth_min = 100.0
        bandwidth_max = 1000.0
        
        # Senaryo üretimi
        attempts = 0
        max_attempts = self.num_scenarios * 10  # Sonsuz döngü önleme
        
        while len(scenarios) < self.num_scenarios and attempts < max_attempts:
            attempts += 1
            
            # Rastgele S-D çifti seç
            source = random.choice(nodes)
            target = random.choice(nodes)
            
            # Aynı düğüm olamaz ve path olmalı
            if source == target:
                continue
            
            if not nx.has_path(self.graph, source, target):
                continue
            
            # Rastgele bandwidth seç (100-1000 Mbps)
            # Farklı değerler için: 100, 200, 300, ..., 1000 gibi dağılım
            bandwidth = random.uniform(bandwidth_min, bandwidth_max)
            bandwidth = round(bandwidth, 1)  # 1 ondalık basamak
            
            scenario = (source, target, bandwidth)
            
            # Duplicate kontrolü
            if scenario not in scenarios:
                scenarios.append(scenario)
                logger.debug(
                    "Generated scenario %s/%s: S=%s, D=%s, B=%.1f Mbps",
                    len(scenarios), self.num_scenarios, source, target, bandwidth
                )
        
        if len(scenarios) < self.num_scenarios:
            logger.warning(
                "Could only generate %s scenarios (requested %s)",
                len(scenarios), self.num_scenarios
            )
        
        logger.info(
            "Generated %s scenarios successfully",
            len(scenarios)
        )
        
        return scenarios


def generate_scenarios_for_experiment(
    graph: nx.Graph,
    num_scenarios: int = 20,
    seed: int = 42
) -> List[Tuple[int, int, float]]:
    """
    Experiment için senaryo üretir.
    
    Args:
        graph: NetworkX graph objesi
        num_scenarios: Senaryo sayısı (varsayılan: 20)
        seed: Rastgele tohum
        
    Returns:
        (source, target, bandwidth) tuple'larının listesi
    """
    generator = ScenarioGenerator(graph, num_scenarios, seed)
    return generator.generate_scenarios()


if __name__ == "__main__":
    # Test için
    from src.network.generator import RandomNetworkGenerator
    
    print("=" * 60)
    print("BSM307 - Scenario Generator Test")
    print("=" * 60)
    
    # Graph oluştur
    gen = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    graph = gen.generate()
    graph = gen.attach_attributes(graph)
    
    print(f"\nGraph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    
    # Senaryoları üret
    scenario_gen = ScenarioGenerator(graph, num_scenarios=20, seed=42)
    scenarios = scenario_gen.generate_scenarios()
    
    print(f"\n✅ Generated {len(scenarios)} scenarios:")
    for i, (s, d, b) in enumerate(scenarios, 1):
        print(f"  {i:2d}. S={s:3d}, D={d:3d}, B={b:6.1f} Mbps")
