from typing import Generic, TypedDict, TypeVar

T = TypeVar("T")
NameT = TypeVar("NameT", bound=str)


class Packet(TypedDict, Generic[NameT, T]):
    name: NameT
    params: T
