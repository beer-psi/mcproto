from typing import Literal, TypedDict
from uuid import UUID

from mcproto.packets.base import Packet
from mcproto.packets.common import SignedProperty


class LoginDisconnectedS2CParams(TypedDict):
    reason: str
    """JSON text component."""


class LoginDisconnectedS2CPacket(
    Packet[Literal["disconnect"], LoginDisconnectedS2CParams]
):
    pass


class LoginHelloS2CParams(TypedDict):
    serverId: str
    publicKey: bytes
    varifyToken: bytes
    shouldAuthenticate: bool


class LoginHelloS2CPacket(Packet[Literal["encryption_begin"], LoginHelloS2CParams]):
    pass


class LoginSuccessS2CParams(TypedDict):
    uuid: UUID
    username: str
    properties: list[SignedProperty]


class LoginSuccessS2CPacket(Packet[Literal["login_success"], LoginSuccessS2CParams]):
    pass


class LoginCompressionS2CParams(TypedDict):
    threshold: int


class LoginCompressionS2CPacket(Packet[Literal["compress"], LoginCompressionS2CParams]):
    pass


class LoginQueryRequestS2CParams(TypedDict):
    messageId: int
    channel: str
    data: bytes


class LoginQueryRequestS2CPacket(
    Packet[Literal["login_plugin_request"], LoginQueryRequestS2CParams]
):
    pass
