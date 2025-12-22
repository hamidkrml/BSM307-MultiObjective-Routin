"""
Yol uygunluk kontrolü
BSM307 - Güz 2025
"""

from typing import Iterable

import networkx as nx

from ..utils.logger import get_logger

logger = get_logger(__name__)


class PathValidator:
    """Yol uygunluk kontrolü için temel iskelet."""

    def __init__(self, graph: nx.Graph):
        self.graph = graph

    def is_simple_path(self, path: Iterable[int]) -> bool:
        """
        S-D yolu döngü içeriyor mu kontrol eder.
        
        Basit path (simple path): Aynı düğümden birden fazla geçmeyen path.
        
        Args:
            path: Kontrol edilecek path (düğüm listesi)
            
        Returns:
            True eğer path basit (döngü yok), False aksi halde
        """
        path_list = list(path)
        
        # Boş veya tek düğümlü path her zaman basittir
        if len(path_list) <= 1:
            return True
        
        visited = set()
        for node in path_list:
            if node in visited:
                logger.debug("Path has cycle at node=%s", node)
                return False
            visited.add(node)
        
        logger.debug("Path is simple (no cycles): %s", path_list)
        return True

    def has_capacity(self, path: Iterable[int], required_bandwidth: float) -> bool:
        """
        Path üzerindeki tüm edge'lerin istenen bandwidth'i karşılayıp karşılamadığını kontrol eder.
        
        Her edge'in bandwidth attribute'u required_bandwidth'den büyük veya eşit olmalı.
        
        Args:
            path: Kontrol edilecek path (düğüm listesi)
            required_bandwidth: İstenen minimum bandwidth (Mbps)
            
        Returns:
            True eğer tüm edge'ler yeterli kapasiteye sahip, False aksi halde
        """
        path_list = list(path)
        
        # Boş veya tek düğümlü path için kapasite kontrolü gerekmez
        if len(path_list) <= 1:
            logger.debug("Path too short for capacity check: %s", path_list)
            return True
        
        # Path üzerindeki her edge'i kontrol et
        for i in range(len(path_list) - 1):
            u = path_list[i]
            v = path_list[i + 1]
            
            # Edge'in graf'ta olup olmadığını kontrol et
            if not self.graph.has_edge(u, v):
                logger.warning("Edge (%s, %s) does not exist in graph", u, v)
                return False
            
            # Edge'in bandwidth attribute'unu al
            edge_bandwidth = self.graph.edges[u, v].get("bandwidth", 0.0)
            
            # Bandwidth kontrolü
            if edge_bandwidth < required_bandwidth:
                logger.debug(
                    "Edge (%s, %s) has insufficient bandwidth: %.1f < %.1f Mbps",
                    u,
                    v,
                    edge_bandwidth,
                    required_bandwidth,
                )
                return False
        
        logger.debug(
            "Path has sufficient capacity for bandwidth=%.1f Mbps: %s",
            required_bandwidth,
            path_list,
        )
        return True

