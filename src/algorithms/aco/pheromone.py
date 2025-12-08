"""
Feromon modeli
BSM307 - Güz 2025
"""

from typing import Any

from ...utils.logger import get_logger

logger = get_logger(__name__)


class PheromoneModel:
    """Feromon matrisini yöneten basit iskelet."""

    def __init__(self, graph: Any, initial: float = 1.0, rho: float = 0.5):
        self.graph = graph
        self.initial = initial
        self.rho = rho
        logger.info("Initialized PheromoneModel initial=%s rho=%s", initial, rho)

    def evaporate(self) -> None:
        """TODO: Tüm kenarlarda buharlaşma uygula."""
        logger.debug("Evaporation step (placeholder)")

    def deposit(self, path: Any, quality: float) -> None:
        """TODO: Yola göre feromon birikimi."""
        logger.debug("Depositing pheromone for path with quality=%s", quality)

