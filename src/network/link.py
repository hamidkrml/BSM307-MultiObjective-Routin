"""
Bağ modeli
BSM307 - Güz 2025
"""

from dataclasses import dataclass, field
from typing import Dict, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Link:
    """Ağ bağlantısı için temel model."""

    source: int
    target: int
    attributes: Dict[str, Any] = field(default_factory=dict)

    def bandwidth(self) -> float:
        """TODO: Gbps cinsinden bant genişliğini döndür."""
        return float(self.attributes.get("bandwidth", 0.0))

    def delay(self) -> float:
        """TODO: Bağ gecikmesini döndür."""
        return float(self.attributes.get("delay", 0.0))

    def reliability(self) -> float:
        """TODO: Bağ güvenilirliğini döndür."""
        return float(self.attributes.get("reliability", 1.0))

