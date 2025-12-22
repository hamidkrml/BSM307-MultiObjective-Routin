"""
Kaynak maliyeti
BSM307 - Güz 2025
"""

from typing import Iterable, List, Tuple, Union

import networkx as nx

from ..utils.logger import get_logger

logger = get_logger(__name__)


def bandwidth_cost(
    path_bandwidths: Union[Iterable[float], None] = None,
    graph: Union[nx.Graph, None] = None,
    path: Union[List[int], None] = None,
) -> float:
    """
    Path üzerindeki tüm edge'ler için kaynak maliyeti hesaplar: 1Gbps / BW.
    
    Her edge için: cost = 1.0 / bandwidth (Gbps cinsinden)
    Toplam maliyet = tüm edge maliyetlerinin toplamı
    
    İki kullanım şekli:
    1. path_bandwidths parametresi ile: Doğrudan bandwidth değerleri listesi (Mbps)
    2. graph ve path parametreleri ile: Graph'tan path üzerindeki edge bandwidth'lerini çıkarır
    
    Args:
        path_bandwidths: Path üzerindeki edge bandwidth değerleri (Mbps)
        graph: NetworkX graph objesi (path ile birlikte kullanılır)
        path: Düğüm listesi [u1, u2, u3, ...] (graph ile birlikte kullanılır)
        
    Returns:
        Toplam kaynak maliyeti (1Gbps / BW toplamı)
    """
    if path_bandwidths is not None:
        # Direkt bandwidth değerleri verilmiş (Mbps)
        costs = []
        for bw in path_bandwidths:
            bw_gbps = float(bw) / 1000.0  # Mbps'den Gbps'e çevir
            cost = (1.0 / bw_gbps) if bw_gbps > 0 else float("inf")
            costs.append(cost)
        total = float(sum(costs))
        logger.debug("Computed bandwidth costs=%s total=%.4f from bandwidths list", costs, total)
        return total
    
    if graph is not None and path is not None:
        # Graph ve path verilmiş, edge bandwidth'lerini çıkar
        path_list = list(path)
        if len(path_list) <= 1:
            logger.debug("Path too short for bandwidth cost calculation: %s", path_list)
            return 0.0
        
        total = 0.0
        for i in range(len(path_list) - 1):
            u = path_list[i]
            v = path_list[i + 1]
            
            if graph.has_edge(u, v):
                edge_bandwidth_mbps = graph.edges[u, v].get("bandwidth", 0.0)
                edge_bandwidth_gbps = float(edge_bandwidth_mbps) / 1000.0  # Mbps'den Gbps'e çevir
                cost = (1.0 / edge_bandwidth_gbps) if edge_bandwidth_gbps > 0 else float("inf")
                total += cost
            else:
                logger.warning("Edge (%s, %s) does not exist in graph", u, v)
                return float("inf")
        
        logger.debug("Computed bandwidth cost=%.4f from path %s", total, path_list)
        return total
    
    logger.error("Either path_bandwidths or (graph, path) must be provided")
    return float("inf")


def weighted_sum(
    delay: float,
    reliability_cost: float,
    resource_cost: float,
    weights: Tuple[float, float, float],
) -> float:
    """
    Ağırlıklı toplam maliyet fonksiyonu.
    
    Formül: w1 * delay + w2 * reliability_cost + w3 * resource_cost
    
    Args:
        delay: Toplam gecikme (ms)
        reliability_cost: Güvenilirlik maliyeti (-log(R))
        resource_cost: Kaynak maliyeti (1Gbps/BW toplamı)
        weights: (w_delay, w_reliability, w_resource) ağırlık tuple'ı
        
    Returns:
        Ağırlıklı toplam skor
    """
    wd, wr, wc = weights
    
    # Ağırlık doğrulaması
    if len(weights) != 3:
        logger.error("Weights must be a tuple of 3 values, got %s", weights)
        return float("inf")
    
    # Negatif ağırlık kontrolü
    if wd < 0 or wr < 0 or wc < 0:
        logger.warning("Negative weights detected: delay=%.2f, reliability=%.2f, resource=%.2f", wd, wr, wc)
    
    # Ağırlıklı toplam hesapla
    score = wd * float(delay) + wr * float(reliability_cost) + wc * float(resource_cost)
    
    logger.debug(
        "Weighted sum: delay=%.2f (w=%.2f) + reliability=%.4f (w=%.2f) + resource=%.4f (w=%.2f) = %.4f",
        delay,
        wd,
        reliability_cost,
        wr,
        resource_cost,
        wc,
        score,
    )
    
    return float(score)

