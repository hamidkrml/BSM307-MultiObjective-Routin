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
        """TODO: Kenar kapasitesi kontrolü."""
        logger.debug("Capacity check placeholder for bandwidth=%s", bandwidth)
        return True
