from typing import Literal, TypedDict

from mcproto.packets.base import Packet

__all__ = (
    "CommonPongC2SParams",
    "CommonPongC2SPacket",
)


class CommonPongC2SParams(TypedDict):
    id: int


class CommonPongC2SPacket(Packet[Literal["pong"], CommonPongC2SParams]):
    pass
