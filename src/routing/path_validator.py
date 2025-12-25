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
        """TODO: S-D yolu döngü içeriyor mu kontrol et."""
        visited = set()
        for node in path:
            if node in visited:
                logger.debug("Path has cycle at node=%s", node)
                return False
            visited.add(node)
        return True

    def has_capacity(self, path: Iterable[int], bandwidth: float) -> bool:
        """
        Path üzerindeki tüm edge'lerin istenen bandwidth'i karşılayıp karşılamadığını kontrol eder.
        
        Args:
            path: Kontrol edilecek path (düğüm listesi)
            bandwidth: İstenen minimum bandwidth (Mbps)
            
        Returns:
            True eğer tüm edge'ler yeterli kapasiteye sahip, False aksi halde
        """
        path_list = list(path)
        
        if len(path_list) <= 1:
            logger.debug("Path too short for capacity check: %s", path_list)
            return True
        
        for i in range(len(path_list) - 1):
            u = path_list[i]
            v = path_list[i + 1]
            
            if not self.graph.has_edge(u, v):
                logger.warning("Edge (%s, %s) does not exist in graph", u, v)
                return False
            
            edge_bandwidth = self.graph.edges[u, v].get("bandwidth", 0.0)
            
            if edge_bandwidth < bandwidth:
                logger.debug(
                    "Edge (%s, %s) has insufficient bandwidth: %.1f < %.1f Mbps",
                    u, v, edge_bandwidth, bandwidth
                )
                return False
        
        logger.debug(
            "Path has sufficient capacity for bandwidth=%.1f Mbps: %s",
            bandwidth, path_list
        )
        return True

