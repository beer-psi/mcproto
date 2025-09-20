from typing import Literal, TypedDict

from mcproto.packets.base import Packet

__all__ = (
    "ReadyC2SParams",
    "ReadyC2SPacket",
)


class ReadyC2SParams(TypedDict):
    pass


class ReadyC2SPacket(Packet[Literal["finish_configuration"], ReadyC2SParams]):
    pass
