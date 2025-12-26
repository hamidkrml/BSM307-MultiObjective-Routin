"""
Toplam gecikme metriği
BSM307 - Güz 2025
"""

from typing import Iterable, List, Union

import networkx as nx

from ..utils.logger import get_logger

logger = get_logger(__name__)


def total_delay(
    path_delays: Union[Iterable[float], None] = None,
    graph: Union[nx.Graph, None] = None,
    path: Union[List[int], None] = None,
) -> float:
    """
    Path üzerindeki tüm edge delay'lerini toplar.
    
    İki kullanım şekli:
    1. path_delays parametresi ile: Doğrudan delay değerleri listesi
    2. graph ve path parametreleri ile: Graph'tan path üzerindeki edge delay'lerini çıkarır
    
    Args:
        path_delays: Path üzerindeki edge delay değerleri (ms)
        graph: NetworkX graph objesi (path ile birlikte kullanılır)
        path: Düğüm listesi [u1, u2, u3, ...] (graph ile birlikte kullanılır)
        
    Returns:
        Toplam gecikme (ms)
    """
    if path_delays is not None:
        # Direkt delay değerleri verilmiş
        delay = float(sum(path_delays))
        logger.debug("Computed total delay from delays list: %.2f ms", delay)
        return delay
    
    if graph is not None and path is not None:
        # Graph ve path verilmiş, edge delay'lerini çıkar
        path_list = list(path)
        if len(path_list) <= 1:
            logger.debug("Path too short for delay calculation: %s", path_list)
            return 0.0
        
        total = 0.0
        for i in range(len(path_list) - 1):
            u = path_list[i]
            v = path_list[i + 1]
            
            if graph.has_edge(u, v):
                edge_delay = graph.edges[u, v].get("delay", 0.0)
                total += float(edge_delay)
            else:
                logger.warning("Edge (%s, %s) does not exist in graph", u, v)
        
        logger.debug("Computed total delay from path %s: %.2f ms", path_list, total)
        return total
    
    logger.error("Either path_delays or (graph, path) must be provided")
    return 0.0

