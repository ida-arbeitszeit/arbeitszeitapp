"""
Sentinels to represent anonymized values.
"""

from __future__ import annotations

from typing import Final, TypeAlias
from uuid import UUID


class AnonymizedUUID:
    """Marker class for anonymized UUIDs.

    Prefer using the singleton instance ANONYMIZED_UUID instead of creating
    new instances. Identity checks ("is") are the recommended way to detect
    anonymized values.
    """

    __slots__: tuple[str, ...] = ()

    def __repr__(self) -> str:
        return "<ANONYMIZED_UUID>"

    def __bool__(self) -> bool:  # pragma: no cover - defensive
        raise TypeError("AnonymizedUUID cannot be used in a boolean context")


class AnonymizedStr:
    """Marker class for anonymized strings.

    Prefer using the singleton instance ANONYMIZED_STR instead of creating
    new instances. Identity checks ("is") are the recommended way to detect
    anonymized values.
    """

    __slots__: tuple[str, ...] = ()

    def __repr__(self) -> str:
        return "<ANONYMIZED_STR>"

    def __bool__(self) -> bool:  # pragma: no cover - defensive
        raise TypeError("AnonymizedStr cannot be used in a boolean context")


# Singleton sentinel instances (preferred values to use and compare against)
ANONYMIZED_UUID: Final[AnonymizedUUID] = AnonymizedUUID()
ANONYMIZED_STR: Final[AnonymizedStr] = AnonymizedStr()


# Helpful type aliases
MaybeAnonymizedUUID: TypeAlias = UUID | AnonymizedUUID
MaybeAnonymizedStr: TypeAlias = str | AnonymizedStr
