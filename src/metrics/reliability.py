"""
Güvenilirlik maliyeti
BSM307 - Güz 2025
"""

import math
from typing import Iterable

from ..utils.logger import get_logger

logger = get_logger(__name__)


def reliability_cost(path_reliabilities: Iterable[float]) -> float:
    """TODO: Güvenilirlik çarpımını hesapla ve -log(R) döndür."""
    reliability = 1.0
    for r in path_reliabilities:
        reliability *= r
    cost = -math.log(reliability) if reliability > 0 else float("inf")
    logger.debug("Computed reliability=%s cost=%s", reliability, cost)
    return cost
