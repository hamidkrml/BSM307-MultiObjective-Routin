"""
Düğüm modeli
BSM307 - Güz 2025

PDF Gereksinimleri (Bölüm 2.2):
- ProcessingDelay: [0.5 ms - 2.0 ms] arası
- NodeReliability: [0.95, 0.999] arası
"""

from dataclasses import dataclass, field
from typing import Dict, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Node:
    """
    Ağ düğümü için temel model.

    PDF gereksinimlerine göre düğüm özellikleri:
    - processing_delay: İşlem gecikmesi [0.5-2.0 ms]
    - reliability: Düğüm güvenilirliği [0.95-0.999]
    """

    id: int
    attributes: Dict[str, Any] = field(default_factory=dict)

    def processing_delay(self) -> float:
        """
        Düğüme özgü işlem gecikmesini döndürür.

        PDF: ProcessingDelay ∈ [0.5, 2.0] ms
        """
        delay = float(self.attributes.get("processing_delay", 0.0))
        if not (0.5 <= delay <= 2.0):
            logger.warning(f"Node {self.id}: processing_delay {delay} outside PDF range [0.5, 2.0]")
        return delay

    def reliability(self) -> float:
        """
        Düğüme özgü güvenilirliği döndürür.

        PDF: NodeReliability ∈ [0.95, 0.999]
        """
        reliability = float(self.attributes.get("reliability", 1.0))
        if not (0.95 <= reliability <= 0.999):
            logger.warning(f"Node {self.id}: reliability {reliability} outside PDF range [0.95, 0.999]")
        return reliability

    def is_valid(self) -> bool:
        """
        Düğüm özelliklerinin PDF gereksinimlerine uyup uymadığını kontrol eder.
        """
        delay_ok = 0.5 <= self.processing_delay() <= 2.0
        reliability_ok = 0.95 <= self.reliability() <= 0.999
        return delay_ok and reliability_ok

