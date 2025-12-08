"""
Graf yardımcıları
BSM307 - Güz 2025
"""

from typing import Any, Dict, Tuple

import networkx as nx

from .logger import get_logger

logger = get_logger(__name__)


def add_node_attributes(
    graph: nx.Graph, attributes: Dict[int, Dict[str, Any]]
) -> nx.Graph:
    """TODO: Node attribute şeması ve doğrulamasını tamamla."""
    nx.set_node_attributes(graph, attributes)
    logger.debug("Added node attributes for %d nodes", len(attributes))
    return graph


def add_edge_attributes(
    graph: nx.Graph, attributes: Dict[Tuple[int, int], Dict[str, Any]]
) -> nx.Graph:
    """TODO: Edge attribute şeması ve doğrulamasını tamamla."""
    nx.set_edge_attributes(graph, attributes)
    logger.debug("Added edge attributes for %d edges", len(attributes))
    return graph


def compute_path_cost(path: Tuple[int, ...]) -> float:
    """Örnek fonksiyon; gerçek maliyet fonksiyonu metrik modüllerine taşınacak."""
    logger.warning("compute_path_cost is a placeholder")
    return 0.0  # TODO: Metriklere göre maliyeti hesapla
