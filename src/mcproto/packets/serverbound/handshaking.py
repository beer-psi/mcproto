# pyright: reportAny=false
from enum import IntEnum
from typing import Literal, TypedDict

from construct import (
    Bytes,
    Const,
    FocusedSeq,
    Int8ub,
    Int16ub,
    Int32sb,
    Optional,
    Prefixed,
    Rebuild,
    StringEncoded,
    Struct,
    len_,
    this,
)

from mcproto.packets.base import Packet

LegacyServerListPingFormat = Struct(
    "ping"
    / Struct(
        Const(b"\xfe"),
        "payload" / Optional(Const(b"\x01")),
    ),
    "message"
    / Optional(
        Struct(
            Const(b"\xfa"),
            "query_name"
            / FocusedSeq(
                "name",
                "length" / Const(b"\x00\x0b"),
                "name"
                / StringEncoded(Const("MC|PingHost".encode("utf-16-be")), "utf-16-be"),
            ),
            "data"
            / Prefixed(
                Int16ub,
                Struct(
                    "protocol_version" / Int8ub,
                    "hostname"
                    / FocusedSeq(
                        "name",
                        "length" / Rebuild(Int16ub, len_(this.name * 2)),
                        "name" / StringEncoded(Bytes(this.length * 2), "utf-16-be"),
                    ),
                    "port" / Int32sb,
                ),
            ),
        )
    ),
)


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
