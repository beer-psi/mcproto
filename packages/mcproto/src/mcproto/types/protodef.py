from typing import Protocol

from construct import Struct


class MinecraftProtocolDefinition(Protocol):
    """
    The Minecraft protocol definition protocol. Users who wish to use a different
    protocol definition than ProtoDef can implement any object that follows this
    protocol, provided that the `packet` struct returns a Struct with "name"
    and "params", as well as compatible param names.
    """

    class MultiplayerStatePackets(Protocol):
        class PacketContainer(Protocol):
            packet: Struct

        toClient: PacketContainer
        toServer: PacketContainer

    handshaking: MultiplayerStatePackets
    status: MultiplayerStatePackets
    login: MultiplayerStatePackets
    configuration: MultiplayerStatePackets
    play: MultiplayerStatePackets
