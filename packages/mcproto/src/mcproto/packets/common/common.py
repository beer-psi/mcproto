from typing import Literal, TypedDict

from mcproto.packets.base import Packet

__all__ = ("KeepAliveParams", "KeepAlivePacket")


class KeepAliveParams(TypedDict):
    keepAliveId: int


class KeepAlivePacket(Packet[Literal["keep_alive"], KeepAliveParams]):
    pass
