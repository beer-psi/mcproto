from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar

from .types.packet import Packet

T = TypeVar("T")


class Event(ABC):
    """The base class for all mcproto events."""


@dataclass(frozen=True)
class PacketReceived(Event, Generic[T]):
    """A packet was received."""

    packet: Packet[T]


@dataclass(frozen=True)
class CloseConnection(Event):
    """
    The end of a connection caused by an exception (usually :class:`PacketParseError`).

    If this event is received, the connection should simply be closed, since it
    is now in an inconsistent state.
    """

    exc: Exception
