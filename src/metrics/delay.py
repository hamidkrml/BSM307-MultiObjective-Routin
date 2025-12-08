"""
Toplam gecikme metriği
BSM307 - Güz 2025
"""

from typing import Iterable

from ..utils.logger import get_logger

logger = get_logger(__name__)


def total_delay(path_delays: Iterable[float]) -> float:
    """TODO: Path üzerindeki per-edge gecikmeleri topla."""
    delay = float(sum(path_delays))
    logger.debug("Computed total delay=%s", delay)
    return delay
