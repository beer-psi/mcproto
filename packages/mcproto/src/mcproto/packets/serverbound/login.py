from typing import Literal, TypedDict
from uuid import UUID

from mcproto.packets.base import Packet

__all__ = (
    "LoginHelloC2SParams",
    "LoginHelloC2SPacket",
    "EnterConfigurationC2SParams",
    "EnterConfigurationC2SPacket",
)


class LoginHelloC2SParams(TypedDict):
    username: str
    playerUUID: UUID


class LoginHelloC2SPacket(Packet[Literal["login_start"], LoginHelloC2SParams]):
    pass


class EnterConfigurationC2SParams(TypedDict):
    pass


class EnterConfigurationC2SPacket(
    Packet[Literal["login_acknowledged"], EnterConfigurationC2SParams]
):
    pass
