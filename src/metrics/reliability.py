"""
Güvenilirlik maliyeti
BSM307 - Güz 2025
"""

import math
from typing import Iterable, List, Union

import networkx as nx

from ..utils.logger import get_logger

logger = get_logger(__name__)


def reliability_cost(
    path_reliabilities: Union[Iterable[float], None] = None,
    graph: Union[nx.Graph, None] = None,
    path: Union[List[int], None] = None,
) -> float:
    """
    Path üzerindeki tüm edge reliability değerlerini çarpar ve -log(R) maliyetini hesaplar.
    
    İki kullanım şekli:
    1. path_reliabilities parametresi ile: Doğrudan reliability değerleri listesi
    2. graph ve path parametreleri ile: Graph'tan path üzerindeki edge reliability'lerini çıkarır
    
    Args:
        path_reliabilities: Path üzerindeki edge reliability değerleri [0.0-1.0]
        graph: NetworkX graph objesi (path ile birlikte kullanılır)
        path: Düğüm listesi [u1, u2, u3, ...] (graph ile birlikte kullanılır)
        
    Returns:
        Güvenilirlik maliyeti: -log(R) (R = path üzerindeki tüm edge reliability'lerinin çarpımı)
    """
    if path_reliabilities is not None:
        # Direkt reliability değerleri verilmiş
        reliability = 1.0
        for r in path_reliabilities:
            reliability *= float(r)
        cost = -math.log(reliability) if reliability > 0 else float("inf")
        logger.debug("Computed reliability=%.4f cost=%.4f from reliabilities list", reliability, cost)
        return cost
    
    if graph is not None and path is not None:
        # Graph ve path verilmiş, edge reliability'lerini çıkar
        path_list = list(path)
        if len(path_list) <= 1:
            logger.debug("Path too short for reliability calculation: %s", path_list)
            return 0.0
        
        reliability = 1.0
        for i in range(len(path_list) - 1):
            u = path_list[i]
            v = path_list[i + 1]
            
            if graph.has_edge(u, v):
                edge_reliability = graph.edges[u, v].get("reliability", 1.0)
                reliability *= float(edge_reliability)
            else:
                logger.warning("Edge (%s, %s) does not exist in graph", u, v)
                reliability = 0.0
                break
        
        cost = -math.log(reliability) if reliability > 0 else float("inf")
        logger.debug("Computed reliability=%.4f cost=%.4f from path %s", reliability, cost, path_list)
        return cost
    
    logger.error("Either path_reliabilities or (graph, path) must be provided")
    return float("inf")

