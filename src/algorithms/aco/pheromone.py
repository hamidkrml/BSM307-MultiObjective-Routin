"""
Feromon modeli
BSM307 - Güz 2025

Issue #13: Complete PheromoneModel implementation
"""

from typing import List

import networkx as nx

from ...utils.logger import get_logger

logger = get_logger(__name__)


class PheromoneModel:
    """
    Feromon matrisini yöneten model.
    
    Issue #13: Evaporation ve deposit mekanizmaları
    """

    def __init__(self, graph: nx.Graph, initial: float = 1.0, rho: float = 0.1):
        """
        Args:
            graph: NetworkX graph objesi
            initial: Başlangıç feromon değeri (tüm edge'ler için)
            rho: Buharlaşma oranı (evaporation rate) [0.0, 1.0]
        """
        self.graph = graph
        self.initial = initial
        self.rho = rho  # Evaporation rate
        
        # Her edge için feromon değerini tut
        self.pheromone = {}
        for u, v in graph.edges():
            self.pheromone[(u, v)] = initial
            self.pheromone[(v, u)] = initial  # Undirected graph için
        
        logger.info("Initialized PheromoneModel: initial=%.2f, rho=%.2f, edges=%s", 
                   initial, rho, len(self.pheromone))

    def get(self, u: int, v: int) -> float:
        """
        Edge (u, v) için feromon değerini döndür.
        
        Args:
            u: Başlangıç düğümü
            v: Hedef düğümü
            
        Returns:
            Feromon değeri
        """
        return self.pheromone.get((u, v), self.initial)

    def evaporate(self) -> None:
        """
        Issue #13: Tüm edge'lerde feromon buharlaşması uygula.
        
        Formül: τ(t+1) = (1 - ρ) * τ(t)
        ρ = evaporation rate
        """
        for edge in self.pheromone:
            self.pheromone[edge] = (1.0 - self.rho) * self.pheromone[edge]
        
        logger.debug("Applied evaporation: rho=%.2f, min_pheromone=%.4f, max_pheromone=%.4f",
                    self.rho,
                    min(self.pheromone.values()) if self.pheromone else 0.0,
                    max(self.pheromone.values()) if self.pheromone else 0.0)

    def deposit(self, path: List[int], quality: float) -> None:
        """
        Issue #13: Path üzerindeki edge'lere feromon biriktir.
        
        Formül: τ(u,v) += Q / cost
        Q = quality (path kalitesi, düşük cost = yüksek quality)
        cost = path'in toplam maliyeti
        
        Args:
            path: Feromon biriktirilecek path (düğüm listesi)
            quality: Path kalitesi (genellikle 1/cost veya sabit değer)
        """
        if len(path) < 2:
            return
        
        # Path üzerindeki her edge'e feromon ekle
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]
            
            # Her iki yönde de feromon ekle (undirected graph)
            if (u, v) in self.pheromone:
                self.pheromone[(u, v)] += quality
            if (v, u) in self.pheromone:
                self.pheromone[(v, u)] += quality
        
        logger.debug("Deposited pheromone: path=%s, quality=%.4f, edges=%s",
                    path[:5] if len(path) > 5 else path,
                    quality,
                    len(path) - 1)
