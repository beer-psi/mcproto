# pyright: reportAny=false, reportExplicitAny=false
from collections.abc import Generator
from enum import IntEnum
from typing import Any, Literal, cast

import protodef

from .codecs import ADDITIONAL_PROTODEF_TYPES
from .data import MinecraftData
from .exceptions import LocalProtocolError, RemoteProtocolError
from .packets import Packet
from .packets.serverbound.handshaking import ConnectionIntent
from .protocol import MinecraftProtocol
from .types import MinecraftProtocolDefinition, MultiplayerState, TextComponent


class ConnectionType(IntEnum):
    CLIENT = 0
    """This connection is a client talking to a multiplayer server."""

    SERVER = 1
    """This connection is a server handling client connections."""


class ConnectionState(IntEnum):
    OPEN = 1
    """The connection is open."""

    CLOSED = 2
    """
    The connection has closed, either because the client closed it,
    or the remote server has kicked the client.
    """


class MinecraftConnection:
    def __init__(
        self,
        connection_type: ConnectionType,
        protodef: MinecraftProtocolDefinition,
        protocol_version: int,
    ):
        self.is_client: bool = connection_type is ConnectionType.CLIENT
        self._protocol: MinecraftProtocol = MinecraftProtocol(
            protodef, protocol_version, is_client=self.is_client
        )
        self._connection_state: ConnectionState = ConnectionState.OPEN

    @classmethod
    def for_version(cls, version: str, connection_type: ConnectionType):
        mc_data = MinecraftData(version)
        proto = protodef.from_definition(
            mc_data.protocol,
            additional_types=ADDITIONAL_PROTODEF_TYPES,  # pyright: ignore[reportArgumentType]
        )
        proto_version = MinecraftData.pc_versions_by_minecraft_version[version][
            "version"
        ]

        return cls(
            connection_type,
            cast(MinecraftProtocolDefinition, proto),  # pyright: ignore[reportInvalidCast]
            proto_version,
        )

    @property
    def connection_state(self) -> ConnectionState:
        return self._connection_state

    @property
    def multiplayer_state(self) -> MultiplayerState:
        return self._protocol.state

    @multiplayer_state.setter
    def multiplayer_state(self, value: MultiplayerState):
        self._protocol.state = value

    @property
    def protocol(self) -> MinecraftProtocolDefinition:
        return self._protocol.protocol

    @property
    def protocol_version(self) -> int:
        return self._protocol.protocol_version

    def send(self, packet: Packet[Any, Any] | bytes | bytearray) -> bytes:
        """
        Processes a packet for sending. If `packet` is a buffer, it is treated
        as raw packet content, **excluding the packet length prefix**.

        When sending a regular packet, state switching is handled automatically:

        | `packet["name"]`             | Target state                               |
        |------------------------------|--------------------------------------------|
        | `start_configuration`        | :attr:`MultiplayerState.CONFIGURATION`     |
        | `configuration_acknowledged` | :attr:`MultiplayerState.CONFIGURATION`     |
        | `login_acknowledged`         | :attr:`MultiplayerState.CONFIGURATION`     |
        | `finish_configuration`       | :attr:`MultiplayerState.PLAY`              |
        | `set_protocol`               | Depends on `packet["params"]["nextState"]` |

        For `set_protocol`:

        | `nextState`                         | Target state                    |
        |-------------------------------------|---------------------------------|
        | 1 (Status)                          | :attr:`MultiplayerState.STATUS` |
        | 2 (Play)                            | :attr:`MultiplayerState.LOGIN`  |
        | 3 (Transfer)                        | :attr:`MultiplayerState.LOGIN`  |

        Disconnects are also handled automatically: when sending a `disconnect` packet
        during :attr:`MultiplayerState.LOGIN`/:attr:`MultiplayerState.CONFIGURATION`,
        or `kick_disconnect` during :attr:`MultiplayerState.PLAY`, the connection is closed.

        :param packet: the packet to process
        :return: the processed packet's contents
        :type packet: packet or buffer
        :rtype: bytes
        :raises LocalProtocolError: if the packet could not be serialized, or the
            packet exceeds the length limit, or the connection has been closed
        """

        if self._connection_state != ConnectionState.OPEN:
            raise LocalProtocolError(
                f"cannot send packets in state {self._connection_state}"
            )

        data = self._protocol.send_packet(packet)

        if isinstance(packet, dict):
            self._call_packet_handler("send", packet)

        return data

    def send_packet(self, name: str, **params: Any):
        """
        Convenience method to send a packet with name and params. These two calls
        are the same thing:

        ```python
        self.send({"name": "ping", "params": {"id": 42}})
        self.send_packet("ping", id=42)
        ```

        View :meth:`send` for more details on what the method does.
        """

        return self.send({"name": name, "params": params})

    def receive_data(self, data: bytes) -> None:
        """
        Pass some received data to the connection for handling.

        A list of packets that the remote peer sent can be retrieved with
        :meth:`Connection.packets`.

        :param bytes data: The data received from the remote server.
        """

        self._protocol.receive_bytes(data)

    def packets(self) -> Generator[Packet[Any, Any], None, None]:
        """
        Return a generator that provides any events that have been generated by
        network activity.

        Packets that affect the connection's state are handled automatically:
        - `login.compress` sets the compression threshold
        - `handshaking.set_protocol` switches to the target state, provided it's valid
        - `login.disconnect`, `configuration.disconnect` and `play.kick_disconnect` closes
        the connection

        Packets that require sending back matching responses (such as `keep_alive` and `ping`)
        have to be handled manually.

        :raises PacketParseError: if the data received could not be parsed into packets
        """

        for packet in self._protocol.received_packets():
            self._call_packet_handler("receive", packet)

            yield packet

    def set_encryption(self, secret: bytes) -> None:
        """
        Enables encryption on this connection. This cannot be undone.

        This should be called immediately after sending an `encryption_begin` packet.

        :param bytes secret: The shared secret.
        """

        self._protocol.set_encryption(secret)

    def close(self, reason: TextComponent | None = None) -> bytes | None:
        """
        Closes the connection. If this is a server-side connection, a disconnect packet
        will be returned with the provided reason, or "Disconnected" if not provided.

        When the multiplayer state is :attr:`MultiplayerState.LOGIN`, the reason must
        be JSON-serializable.
        """

        if self.is_client:
            self._connection_state = ConnectionState.CLOSED
            return None

        if self._protocol.state not in (
            MultiplayerState.LOGIN,
            MultiplayerState.CONFIGURATION,
            MultiplayerState.PLAY,
        ):
            self._connection_state = ConnectionState.CLOSED
            return None

        if reason is None:
            reason = {"type": "text", "text": "Disconnected"}

        data = self.send_packet(
            "kick_disconnect"
            if self._protocol.state == MultiplayerState.PLAY
            else "disconnect",
            reason=reason,
        )

        return data

    def _call_packet_handler(
        self, direction: Literal["receive", "send"], packet: Packet[Any, Any]
    ):
        handler_name = f"_on_{'client' if self.is_client else 'server'}_{direction}_{self._protocol.state.value}_{packet['name']}"
        handler_fn = getattr(self, handler_name, None)

        if handler_fn is not None:
            handler_fn(packet["params"])

    def _on_handshaking_set_protocol(self, params: Any):
        next_state = params["nextState"]
        exc_type = LocalProtocolError if self.is_client else RemoteProtocolError

        if not isinstance(next_state, int):
            raise exc_type("nextState must be an integer")

        if next_state == ConnectionIntent.STATUS.value:
            self._protocol.state = MultiplayerState.STATUS
        elif next_state in (
            ConnectionIntent.LOGIN.value,
            ConnectionIntent.TRANSFER.value,
        ):
            self._protocol.state = MultiplayerState.LOGIN
        else:
            raise exc_type(f"invalid next state: {next_state}")

    def _on_login_compress(self, params: Any):
        threshold = params["threshold"]
        exc_type = RemoteProtocolError if self.is_client else LocalProtocolError

        if not isinstance(threshold, int):
            raise exc_type("a compress packet with a non-integer threshold")

        self._protocol.set_compression(threshold)

    def _on_disconnect(self, _params: Any):
        self._connection_state = ConnectionState.CLOSED

    # Massive wall of event handlers...

    # Client/Handshaking

    def _on_client_send_handshaking_set_protocol(self, params: Any):
        self._on_handshaking_set_protocol(params)

    # Client/Login

    def _on_client_send_login_login_acknowledged(self, _params: Any):
        self._protocol.state = MultiplayerState.CONFIGURATION

    def _on_client_receive_login_disconnect(self, params: Any):
        self._on_disconnect(params)

    def _on_client_receive_login_compress(self, params: Any):
        self._on_login_compress(params)

    # Client/Configuration

    def _on_client_send_configuration_finish_configuration(self, _params: Any):
        self._protocol.state = MultiplayerState.PLAY

    def _on_client_receive_configuration_disconnect(self, params: Any):
        self._on_disconnect(params)

    # Client/Play

    def _on_client_send_play_configuration_acknowledged(self, _params: Any):
        self._protocol.state = MultiplayerState.CONFIGURATION

    def _on_client_receive_play_kick_disconnect(self, params: Any):
        self._on_disconnect(params)

    def _on_server_receive_handshaking_set_protocol(self, params: Any):
        self._on_handshaking_set_protocol(params)

    # Server/Login

    def _on_server_send_login_disconnect(self, params: Any):
        self._on_disconnect(params)

    def _on_server_send_login_compress(self, params: Any):
        self._on_login_compress(params)

    # Server/Configuration

    def _on_server_send_configuration_disconnect(self, params: Any):
        self._on_disconnect(params)

    def _on_server_send_configuration_finish_configuration(self, _params: Any):
        self._protocol.state = MultiplayerState.PLAY

    # Server/Play

    def _on_server_send_play_start_configuration(self, _params: Any):
        self._protocol.state = MultiplayerState.CONFIGURATION

    def _on_server_send_play_kick_disconnect(self, params: Any):
        self._on_disconnect(params)
