"""
Basit UI giriş noktası
BSM307 - Güz 2025
"""

from typing import Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


def run_app(graph: Any) -> None:
    """TODO: CLI/GUI başlangıcı."""
    logger.info("Launching placeholder UI with graph=%s nodes", getattr(graph, "number_of_nodes", lambda: "?")())
    # TODO: networkx + matplotlib entegrasyonu, S-D seçimi, slider'lar
