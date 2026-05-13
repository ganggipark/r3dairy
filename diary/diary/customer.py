"""Stable customer ID derivation from birth info.

12-char: legacy cache directory (backward compat).
20-char: web URL token (more entropy, ~120 bits).
"""
from __future__ import annotations
import hashlib

from .models import SajuInput


def customer_id(birth: SajuInput, length: int = 12) -> str:
    """sha256(birth_info)[:length]. 12=cache, 20=web token."""
    if not (8 <= length <= 64):
        raise ValueError("length must be 8..64")
    s = (
        f"{birth.year}-{birth.month}-{birth.day}T{birth.hour}:{birth.minute}_"
        f"{birth.gender}_lunar{birth.isLunar}_leap{birth.isLeapMonth}_"
        f"{birth.birthPlace}_true{birth.useTrueSolarTime}"
    )
    return hashlib.sha256(s.encode()).hexdigest()[:length]
