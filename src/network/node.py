"""
Düğüm modeli
BSM307 - Güz 2025
"""

from dataclasses import dataclass, field
from typing import Dict, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Node:
    """Ağ düğümü için temel model."""

    id: int
    attributes: Dict[str, Any] = field(default_factory=dict)

    def processing_delay(self) -> float:
        """TODO: Düğüme özgü işlem gecikmesini döndür."""
        return float(self.attributes.get("processing_delay", 0.0))

    def reliability(self) -> float:
        """TODO: Düğüme özgü güvenilirliği döndür."""
        return float(self.attributes.get("reliability", 1.0))

