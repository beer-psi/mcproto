# pyright: reportAny=false
from enum import IntEnum
from typing import Literal, NotRequired, TypedDict
from typing_extensions import TypeAlias

from construct import (
    Bytes,
    Const,
    FocusedSeq,
    Int8ub,
    Int16ub,
    Int32sb,
    Prefixed,
    Rebuild,
    Select,
    StringEncoded,
    Struct,
    len_,
    this,
)

from mcproto.packets.base import Packet

__all__ = (
    "LegacyServerListPingFormat",
    "LegacyServerListPingPre13Params",
    "LegacyServerListPing14Params",
    "LegacyServerListPingParams",
    "LegacyServerListPingPacket",
    "ConnectionIntent",
    "HandshakeC2SParams",
    "HandshakeC2SPacket",
)


LegacyServerListPingFormat = Select(
    Struct(
        "ping"
        / Struct(
            Const(b"\xfe"),
            "payload" / Const(b"\x01"),
        ),
        "message"
        / Struct(
            Const(b"\xfa"),
            "query_name"
            / FocusedSeq(
                "data",
                "length" / Rebuild(Int16ub, len_(this.data)),
                "data"
                / StringEncoded(Const("MC|PingHost".encode("utf-16-be")), "utf-16-be"),
            ),
            "data"
            / Prefixed(
                Int16ub,
                Struct(
                    "protocol_version" / Int8ub,
                    "hostname"
                    / FocusedSeq(
                        "data",
                        "length" / Rebuild(Int16ub, len_(this.data)),
                        "data" / StringEncoded(Bytes(this.length * 2), "utf-16-be"),
                    ),
                    "port" / Int32sb,
                ),
            ),
        ),
    ),
    Struct("ping" / Struct(Const(b"\xfe"), "payload" / Const(b"\x01"))),
    Struct("ping" / Struct(Const(b"\xfe"))),
)


class PingParams(TypedDict):
    payload: Literal[b"\x01"]


class MCPingHostData(TypedDict):
    protocol_version: int
    hostname: str
    port: int


class MessageParams(TypedDict):
    query_name: Literal["MC|PingHost"]
    data: MCPingHostData


class LegacyServerListPingPre13Params(TypedDict):
    pass


class LegacyServerListPing14Params(TypedDict):
    ping: PingParams
    message: NotRequired[MessageParams]


LegacyServerListPingParams: TypeAlias = (
    LegacyServerListPingPre13Params | LegacyServerListPing14Params
)


class LegacyServerListPingPacket(
    Packet[Literal["legacy_server_list_ping"], LegacyServerListPingParams]
):
    pass


class ConnectionIntent(IntEnum):
    STATUS = 1
    LOGIN = 2
    TRANSFER = 3


class HandshakeC2SParams(TypedDict):
    protocolVersion: int
    serverHost: str
    serverPort: int
    nextState: Literal[1, 2, 3]


class HandshakeC2SPacket(Packet[Literal["set_protocol"], HandshakeC2SParams]):
    pass
