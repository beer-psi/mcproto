from typing import Generic, TypedDict, TypeVar

T = TypeVar("T")


class Packet(TypedDict, Generic[T]):
    name: str
    params: T
