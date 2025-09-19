from typing import Literal, TypedDict

from mcproto.packets.base import Packet


class QueryResponseS2CParams(TypedDict):
    response: str


class QueryResponseS2CPacket(Packet[Literal["server_info"], QueryResponseS2CParams]):
    pass


class PingResultS2CParams(TypedDict):
    time: int


class PingResultS2CPacket(Packet[Literal["ping"], PingResultS2CParams]):
    pass
