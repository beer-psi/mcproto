import hashlib
import uuid

from construct import Bytes, ExprAdapter

UUID: "ExprAdapter[bytes, bytes | int, uuid.UUID, uuid.UUID]" = ExprAdapter(
    Bytes(16),
    lambda data, ctx: uuid.UUID(bytes=data),
    lambda uuid, ctx: uuid.bytes,
)


def create_offline_player_uuid(player_name: str):
    digest = hashlib.md5(
        b"OfflinePlayer:" + player_name.encode("utf-8"), usedforsecurity=False
    ).digest()

    return uuid.UUID(bytes=digest[:16], version=3)
