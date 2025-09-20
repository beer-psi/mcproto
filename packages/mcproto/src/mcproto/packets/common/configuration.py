from typing import Literal, TypedDict

from mcproto.packets.base import Packet
from mcproto.packets.types import VersionedIdentifier

__all__ = ("SelectKnownPacksParams", "SelectKnownPacksPacket")


class SelectKnownPacksParams(TypedDict):
    packs: list[VersionedIdentifier]


class SelectKnownPacksPacket(
    Packet[Literal["select_known_packs"], SelectKnownPacksParams]
):
    pass
