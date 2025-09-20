from typing import Generic, TypedDict, TypeVar

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class SignedProperty(TypedDict):
    name: str
    value: str
    signature: str | None


class VersionedIdentifier(TypedDict):
    namespace: str
    id: str
    version: str


class KeyValuePair(TypedDict, Generic[_KT, _VT]):
    key: _KT
    value: _VT
