from typing import Any, Literal, TypedDict
from uuid import UUID

from mcproto.packets.base import Packet
from mcproto.packets.common import KeyValuePair
from mcproto.types import TextComponent


class CookieRequestS2CParams(TypedDict):
    cookie: str


class CookieRequestS2CPacket(Packet[Literal["cookie_request"], CookieRequestS2CParams]):
    pass


class StoreCookieS2CParams(TypedDict):
    key: str
    value: bytes


class StoreCookieS2CPacket(Packet[Literal["store_cookie"], StoreCookieS2CParams]):
    pass


class CustomPayloadS2CParams(TypedDict):
    channel: str
    data: bytes


class CustomPayloadS2CPacket(Packet[Literal["custom_payload"], CustomPayloadS2CParams]):
    pass


class DisconnectS2CParams(TypedDict):
    reason: TextComponent


class DisconnectS2CPacket(
    Packet[Literal["disconnect", "kick_disconnect"], DisconnectS2CParams]
):
    pass


class KeepAliveS2CParams(TypedDict):
    keepAliveId: int


class KeepAliveS2CPacket(Packet[Literal["keep_alive"], KeepAliveS2CParams]):
    pass


class CommonPingS2CParams(TypedDict):
    id: int


class CommonPingS2CPacket(Packet[Literal["ping"], CommonPingS2CParams]):
    pass


class ResourcePackRemoveS2CParams(TypedDict):
    uuid: UUID | None


class ResourcePackRemoveS2CPacket(
    Packet[Literal["remove_resource_pack"], ResourcePackRemoveS2CParams]
):
    pass


class ResourcePackSendS2CParams(TypedDict):
    uuid: UUID
    url: str
    hash: str
    forced: bool
    promptMessage: TextComponent | None


class ResourcePackSendS2CPacket(
    Packet[Literal["add_resource_pack"], ResourcePackSendS2CParams]
):
    pass


class ServerTransferS2CParams(TypedDict):
    host: str
    port: int


class ServerTransferS2CPacket(Packet[Literal["transfer"], ServerTransferS2CParams]):
    pass


class Tag(TypedDict):
    tagName: str
    entries: list[int]


class TagGroup(TypedDict):
    tagType: str
    tags: list[Tag]


class SynchronizeTagsS2CParams(TypedDict):
    tags: list[TagGroup]


class SynchronizeTagsS2CPacket(Packet[Literal["tags"], SynchronizeTagsS2CParams]):
    pass


class CustomReportDetailsS2CParams(TypedDict):
    details: list[KeyValuePair[str, str]]


class CustomReportDetailsS2CPacket(
    Packet[Literal["custom_report_details"], CustomReportDetailsS2CParams]
):
    pass


class ServerLinkKnownType(TypedDict):
    hasKnownType: Literal[True]
    knownType: Literal[
        "bug_report",
        "community_guidelines",
        "support",
        "status",
        "feedback",
        "community",
        "website",
        "forums",
        "news",
        "announcements",
    ]
    link: str


class ServerLinkUnknownType(TypedDict):
    hasKnownType: Literal[False]
    unknownType: TextComponent
    link: str


class ServerLinksS2CParams(TypedDict):
    links: list[ServerLinkKnownType | ServerLinkUnknownType]


class ServerLinksS2CPacket(Packet[Literal["server_links"], ServerLinksS2CParams]):
    pass


class ClearDialogS2CParams(TypedDict):
    pass


class ClearDialogS2CPacket(Packet[Literal["clear_dialog"], ClearDialogS2CParams]):
    pass


class ShowDialogS2CParams(TypedDict):
    dialog: Any  # pyright: ignore[reportExplicitAny]


class ShowDialogS2CPacket(Packet[Literal["show_dialog"], ShowDialogS2CParams]):
    pass
