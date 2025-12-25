"""
Karınca Kolonisi Optimizasyonu
BSM307 - Güz 2025

Issue #13, #14, #15: Complete ACO implementation
"""

import math
import random
from typing import List, Optional, Sequence, Tuple

import networkx as nx

from ...metrics.delay import total_delay
from ...metrics.reliability import reliability_cost
from ...metrics.resource_cost import bandwidth_cost, weighted_sum
from ...routing.path_validator import PathValidator
from ..aco.pheromone import PheromoneModel
from ...utils.logger import get_logger

logger = get_logger(__name__)


class AntColonyOptimizer:
    """
    Karınca Kolonisi Optimizasyonu ile çok amaçlı rota optimizasyonu.
    
    Issue #13: Pheromone model integration
    Issue #14: Solution construction
    Issue #15: Main ACO loop
    """

    def __init__(
        self,
        graph: nx.Graph,
        source: int,
        target: int,
        weights: Sequence[float] = (0.4, 0.3, 0.3),
        required_bandwidth: float = 500.0,
        alpha: float = 1.0,
        beta: float = 2.0,
        evaporation_rate: float = 0.1,
        num_ants: int = 20,
        initial_pheromone: float = 1.0,
        seed: Optional[int] = None,
    ):
        """
        Args:
            graph: NetworkX graph objesi
            source: Başlangıç düğümü
            target: Hedef düğümü
            weights: (delay_weight, reliability_weight, resource_weight) tuple
            required_bandwidth: Minimum gerekli bandwidth (Mbps)
            alpha: Feromon ağırlığı (pheromone importance)
            beta: Heuristik ağırlığı (heuristic importance)
            evaporation_rate: Feromon buharlaşma oranı (rho)
            num_ants: Her iterasyonda çalıştırılacak karınca sayısı
            initial_pheromone: Başlangıç feromon değeri
            seed: Rastgele tohum (reproducibility için)
        """
        self.graph = graph
        self.source = source
        self.target = target
        self.weights = tuple(weights)
        self.required_bandwidth = required_bandwidth
        self.alpha = alpha
        self.beta = beta
        self.num_ants = num_ants
        
        self.validator = PathValidator(graph)
        self.pheromone_model = PheromoneModel(graph, initial=initial_pheromone, rho=evaporation_rate)
        
        if seed is not None:
            random.seed(seed)
        
        logger.info(
            "Initialized AntColonyOptimizer: source=%s, target=%s, alpha=%.2f, beta=%.2f, ants=%s",
            source, target, alpha, beta, num_ants
        )

    def _heuristic_value(self, u: int, v: int) -> float:
        """
        Edge (u, v) için heuristik değer hesapla.
        
        Heuristik: 1 / (delay + resource_cost)
        Düşük delay ve resource cost = yüksek heuristik değer
        
        Args:
            u: Başlangıç düğümü
            v: Hedef düğümü
            
        Returns:
            Heuristik değer (yüksek = iyi)
        """
        if not self.graph.has_edge(u, v):
            return 0.0
        
        edge_data = self.graph.edges[u, v]
        delay = edge_data.get("delay", 15.0)  # Default: max delay
        bandwidth = edge_data.get("bandwidth", 100.0)  # Default: min bandwidth
        
        # Resource cost: 1 / bandwidth (Gbps)
        bandwidth_gbps = bandwidth / 1000.0
        resource_cost = 1.0 / bandwidth_gbps if bandwidth_gbps > 0 else float("inf")
        
        # Heuristik: 1 / (delay + resource_cost)
        # Düşük delay ve resource = yüksek heuristik
        total_cost = delay + resource_cost
        heuristic = 1.0 / total_cost if total_cost > 0 else 0.0
        
        return heuristic

    def _select_next_node(self, current: int, visited: set) -> Optional[int]:
        """
        Issue #14: Mevcut düğümden sonraki düğümü seç (feromon + heuristik).
        
        Olasılık: P(u,v) = [τ(u,v)]^α * [η(u,v)]^β / Σ
        
        Args:
            current: Mevcut düğüm
            visited: Ziyaret edilmiş düğümler (döngü önleme)
            
        Returns:
            Seçilen sonraki düğüm veya None
        """
        neighbors = [n for n in self.graph.neighbors(current) if n not in visited]
        
        if not neighbors:
            return None
        
        # Her komşu için olasılık hesapla
        probabilities = []
        for neighbor in neighbors:
            pheromone = self.pheromone_model.get(current, neighbor)
            heuristic = self._heuristic_value(current, neighbor)
            
            # P(u,v) = [τ(u,v)]^α * [η(u,v)]^β
            prob = (pheromone ** self.alpha) * (heuristic ** self.beta)
            probabilities.append((neighbor, prob))
        
        # Toplam olasılığı hesapla (normalizasyon için)
        total_prob = sum(prob for _, prob in probabilities)
        
        if total_prob == 0:
            # Tüm olasılıklar 0, rastgele seç
            return random.choice(neighbors)
        
        # Normalize et ve rastgele seç
        r = random.random() * total_prob
        cumulative = 0.0
        for neighbor, prob in probabilities:
            cumulative += prob
            if r <= cumulative:
                return neighbor
        
        # Fallback: son komşu
        return neighbors[-1]

    def construct_solution(self) -> Optional[List[int]]:
        """
        Issue #14: Bir karınca için path oluştur (feromon + heuristik).
        
        Strateji:
        1. Source'tan başla
        2. Her adımda: feromon ve heuristik bilgisiyle komşu seç
        3. Target'a ulaşana kadar devam et
        4. Döngü önleme (visited set)
        5. Eğer target'a ulaşılamazsa, shortest path ile tamamla
        
        Returns:
            Oluşturulan path veya None (yol bulunamazsa)
        """
        path = [self.source]
        visited = {self.source}
        current = self.source
        max_length = self.graph.number_of_nodes()  # Sonsuz döngü önleme
        
        for _ in range(max_length):
            if current == self.target:
                # Target'a ulaşıldı
                if self.validator.is_simple_path(path) and \
                   self.validator.has_capacity(path, self.required_bandwidth):
                    return path
                else:
                    # Geçersiz path, shortest path ile tamamla
                    if nx.has_path(self.graph, self.source, self.target):
                        return nx.shortest_path(self.graph, self.source, self.target)
                    return None
            
            # Sonraki düğümü seç
            next_node = self._select_next_node(current, visited)
            
            if next_node is None:
                # Yol bulunamadı, shortest path ile tamamla
                if nx.has_path(self.graph, current, self.target):
                    remaining_path = nx.shortest_path(self.graph, current, self.target)
                    # Path'i birleştir (current'ı tekrar ekleme)
                    path.extend(remaining_path[1:])
                    # Geçerliliği kontrol et
                    if self.validator.is_simple_path(path) and \
                       self.validator.has_capacity(path, self.required_bandwidth):
                        return path
                    # Geçersizse, baştan shortest path döndür
                    if nx.has_path(self.graph, self.source, self.target):
                        return nx.shortest_path(self.graph, self.source, self.target)
                return None
            
            path.append(next_node)
            visited.add(next_node)
            current = next_node
        
        # Target'a ulaşılamadı, shortest path ile tamamla
        if nx.has_path(self.graph, current, self.target):
            remaining_path = nx.shortest_path(self.graph, current, self.target)
            path.extend(remaining_path[1:])
            if self.validator.is_simple_path(path) and \
               self.validator.has_capacity(path, self.required_bandwidth):
                return path
        
        # Son çare: shortest path
        if nx.has_path(self.graph, self.source, self.target):
            return nx.shortest_path(self.graph, self.source, self.target)
        
        return None

    def _path_cost(self, path: List[int]) -> float:
        """
        Path için toplam maliyet hesapla (fitness benzeri).
        
        Args:
            path: Path (düğüm listesi)
            
        Returns:
            Toplam maliyet (düşük = iyi)
        """
        if not self.validator.is_simple_path(path) or \
           not self.validator.has_capacity(path, self.required_bandwidth):
            return float("inf")
        
        delay = total_delay(graph=self.graph, path=path)
        rel_cost = reliability_cost(graph=self.graph, path=path)
        res_cost = bandwidth_cost(graph=self.graph, path=path)
        
        cost = weighted_sum(delay, rel_cost, res_cost, self.weights)
        return cost

    def run(self, iterations: int = 50) -> Tuple[List[int], float]:
        """
        Issue #15: ACO ana döngüsü.
        
        Her iterasyonda:
        1. N karınca path oluşturur
        2. En iyi path bulunur
        3. Feromon buharlaşır
        4. En iyi path'e feromon eklenir
        
        Args:
            iterations: İterasyon sayısı
            
        Returns:
            (best_path, best_cost) tuple
        """
        logger.info("Running ACO for %s iterations with %s ants", iterations, self.num_ants)
        
        best_path = None
        best_cost = float("inf")
        
        for iteration in range(iterations):
            # Bu iterasyondaki tüm path'ler
            iteration_paths = []
            
            # N karınca path oluştur
            for ant in range(self.num_ants):
                path = self.construct_solution()
                if path is not None:
                    cost = self._path_cost(path)
                    iteration_paths.append((path, cost))
                    
                    # En iyiyi güncelle
                    if cost < best_cost:
                        best_path = path
                        best_cost = cost
                        logger.info(
                            "Iteration %s, Ant %s: New best cost=%.4f (path length=%s)",
                            iteration + 1, ant + 1, best_cost, len(path)
                        )
            
            # Feromon buharlaşması
            self.pheromone_model.evaporate()
            
            # En iyi path'e feromon ekle (veya tüm path'lere)
            if iteration_paths:
                # Sadece en iyi path'e feromon ekle (elitist strategy)
                if best_path:
                    quality = 1.0 / best_cost if best_cost > 0 else 1.0
                    self.pheromone_model.deposit(best_path, quality)
        
        if best_path is None:
            logger.error("ACO could not find a valid path!")
            return [], float("inf")
        
        logger.info("ACO completed. Best cost: %.4f, path: %s", best_cost, best_path)
        return best_path, best_cost

