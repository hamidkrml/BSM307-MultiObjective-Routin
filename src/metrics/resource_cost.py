"""
Kaynak maliyeti
BSM307 - Güz 2025
"""

from typing import Iterable

from ..utils.logger import get_logger

logger = get_logger(__name__)


def bandwidth_cost(path_bandwidths: Iterable[float]) -> float:
    """Kaynak maliyeti: 1Gbps / BW."""
    costs = []
    for bw in path_bandwidths:
        cost = (1.0 / bw) if bw > 0 else float("inf")
        costs.append(cost)
    total = float(sum(costs))
    logger.debug("Computed bandwidth costs=%s total=%s", costs, total)
    return total


def weighted_sum(delay: float, reliability: float, resource: float, weights: tuple) -> float:
    """TODO: Ağırlık doğrulaması ve normalizasyon stratejisi ekle."""
    wd, wr, wc = weights
    score = wd * delay + wr * reliability + wc * resource
    logger.debug("Weighted sum score=%s", score)
    return float(score)
