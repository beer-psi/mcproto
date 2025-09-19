from typing import Any, Literal, TypedDict

from mcproto.packets.base import Packet
from mcproto.packets.common import VersionedIdentifier


class ReadyS2CParams(TypedDict):
    pass


class ReadyS2CPacket(Packet[Literal["finish_configuration"], ReadyS2CParams]):
    pass


class ResetChatS2CParams(TypedDict):
    pass


class ResetChatS2CPacket(Packet[Literal["reset_chat"], ResetChatS2CParams]):
    pass


class RegistryEntry(TypedDict):
    key: str
    value: Any | None  # pyright: ignore[reportExplicitAny]


class DynamicRegistriesS2CParams(TypedDict):
    id: str
    entries: list[RegistryEntry]


class DynamicRegistriesS2CPacket(
    Packet[Literal["registry_data"], DynamicRegistriesS2CParams]
):
    pass


class SelectKnownPacksS2CParams(TypedDict):
    packs: list[VersionedIdentifier]


class SelectKnownPacksS2CPacket(
    Packet[Literal["select_known_packs"], SelectKnownPacksS2CParams]
):
    pass


class FeaturesS2CParams(TypedDict):
    features: list[str]


class FeaturesS2CPacket(Packet[Literal["feature_flags"], FeaturesS2CParams]):
    pass
