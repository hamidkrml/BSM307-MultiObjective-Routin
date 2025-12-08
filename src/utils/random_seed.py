"""
Rastgele tohum yardımcıları
BSM307 - Güz 2025
"""

import random
from typing import Optional

import numpy as np

from .logger import get_logger

logger = get_logger(__name__)


def set_seed(seed: int, *, deterministic: bool = False) -> None:
    """TODO: Gerekirse ek RNG kitaplıkları için tohum ekle."""
    logger.info("Setting random seed: %s (deterministic=%s)", seed, deterministic)
    random.seed(seed)
    np.random.seed(seed)
    if deterministic:
        logger.debug("Deterministic mode requested (placeholder).")
    # TODO: Ek kütüphaneler (torch, jax) için tohum ekle


def get_seed_from_env(env_var: str = "EXPERIMENT_SEED") -> Optional[int]:
    """TODO: Ortam değişkeninden tohum okuma ve doğrulama."""
    return None
