from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar

from .packets import Packet

T = TypeVar("T")
NameT = TypeVar("NameT", bound=str)


class Event(ABC):
    """The base class for all mcproto events."""


@dataclass(frozen=True)
class PacketReceived(Event, Generic[NameT, T]):
    """A packet was received."""

    packet: Packet[NameT, T]


@dataclass(frozen=True)
class ConnectionEnded(Event):
    """
    The end of a connection caused by an exception (usually :class:`PacketParseError`).

    If this event is received, the connection should simply be closed, since it
    is now in an inconsistent state.
    """

    exc: Exception
