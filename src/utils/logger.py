"""
Logger yardımcıları
BSM307 - Güz 2025
"""

import logging
from typing import Optional


def configure_root_logger(level: int = logging.INFO) -> None:
    """TODO: Proje genelinde ortak logging formatını tamamla."""
    if logging.getLogger().handlers:
        return
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Tutarlı logger üretir."""
    configure_root_logger()
    return logging.getLogger(name)

