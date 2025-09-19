# pyright: reportAny=false
import io
import json
import zlib
from collections.abc import Generator, Mapping
from pathlib import Path
from typing import Any, cast

import protodef
from construct import ConstructError, Int16sb, IntegerError, StreamError
from cryptography.hazmat.primitives.ciphers import (
    Cipher,
    CipherContext,
    algorithms,
    modes,
)
from protodef.datatypes.varint import SizedVarInt

from .codecs import ADDITIONAL_PROTODEF_TYPES
from .exceptions import (
    EncryptionSetTwiceError,
    LocalProtocolError,
    PacketParseError,
)
from .packets.serverbound.handshaking import LegacyServerListPingFormat
from .types import MinecraftProtocolDefinition, MultiplayerState, Packet

_MINECRAFT_DATA_DIR = Path(__file__).parent / "data"


class Buffer:
    # Copied from https://github.com/python-hyper/wsproto
    # SPDX-License-Identifier: MIT

    def __init__(self, initial_bytes: bytes | None = None) -> None:
        self.buffer: bytearray = bytearray()
        self.bytes_used: int = 0

        if initial_bytes is not None:
            self.feed(initial_bytes)

    def feed(self, new_bytes: bytes) -> None:
        self.buffer += new_bytes  # += is somehow faster than .extend

    def consume_at_most(self, nbytes: int) -> bytes:
        if not nbytes:
            return bytearray()

        data = self.buffer[self.bytes_used : self.bytes_used + nbytes]
        self.bytes_used += len(data)
        return data

    def consume_exactly(self, nbytes: int) -> bytes | None:
        if len(self.buffer) - self.bytes_used < nbytes:
            return None

        return self.consume_at_most(nbytes)

    @property
    def consumed(self):
        return self.buffer[: self.bytes_used]

    def return_bytes(self, nbytes: int):
        self.bytes_used -= nbytes

    def commit(self) -> None:
        # In CPython 3.4+, del[:n] is amortized O(n), *not* quadratic
        del self.buffer[: self.bytes_used]
        self.bytes_used = 0

    def rollback(self) -> None:
        self.bytes_used = 0

    def __len__(self) -> int:
        return len(self.buffer)


class MinecraftProtocol:
    """Minecraft sans-IO multiplayer packet protocol."""

    def __init__(
        self,
        protocol: MinecraftProtocolDefinition,
        protocol_version: int,
        state: MultiplayerState = MultiplayerState.HANDSHAKING,
        *,
        is_client: bool,
    ):
        """
        Constructor.

        :param protocol: The Minecraft packet protocol to use.
        :param int protocol_version: The version of the provided protocol.
        :param state: The initial state of the protcol.
        :param bool is_client: Whether this is a client connection.
        """

        self.is_client: bool = is_client
        self.protocol: MinecraftProtocolDefinition = protocol
        self.protocol_version: int = protocol_version
        self.state: MultiplayerState = state

        self._cipher: Cipher[modes.CFB8] | None = None
        self._encryptor: CipherContext | None = None

        self._frame_decoder: FrameDecoder = FrameDecoder()
        self._decompression_handler: DecompressionHandler = DecompressionHandler(
            self._frame_decoder
        )
        self._decryption_handler: DecryptionHandler = DecryptionHandler(
            self._decompression_handler
        )
        self._compression_threshold: int = -1

        # we only set this once
        self._frame_decoder.recognize_legacy_ping = (
            not is_client and state == MultiplayerState.HANDSHAKING
        )

        self._parse_more: Generator[Packet[Any] | None, None, None] = (  # pyright: ignore[reportExplicitAny]
            self._parse_more_gen()
        )

    @classmethod
    def for_version(
        cls,
        version: str,
        state: MultiplayerState = MultiplayerState.HANDSHAKING,
        *,
        is_client: bool,
    ):
        """
        Creates a :class:`PacketProtocol` instance for the provided version using the
        [minecraft-data] repository.

        [minecraft-data]: https://github.com/PrismarineJS/minecraft-data
        """

        proto = protodef.from_file(
            _MINECRAFT_DATA_DIR / "data" / "pc" / version / "protocol.json",
            additional_types=ADDITIONAL_PROTODEF_TYPES,  # pyright: ignore[reportArgumentType]
        )

        with (
            _MINECRAFT_DATA_DIR / "data" / "pc" / "common" / "protocolVersions.json"
        ).open("rb") as f:
            data = json.load(f)
            protocol_version = next(
                v["version"] for v in data if v["minecraftVersion"] == version
            )

        return cls(
            cast(MinecraftProtocolDefinition, proto),  # pyright: ignore[reportInvalidCast]
            protocol_version,
            state,
            is_client=is_client,
        )

    def _parse_more_gen(self) -> Generator["Packet[Any] | None", None, None]:  # pyright: ignore[reportExplicitAny]
        while True:
            data = self._decryption_handler.process_buffer()

            if data is None:
                yield None
                continue

            if self._frame_decoder.recognize_legacy_ping and data[0] == 0xFE:
                yield {
                    "name": "legacy_server_list_ping",
                    "params": {
                        k: v
                        for k, v in LegacyServerListPingFormat.parse(data).items()
                        if not k.startswith("_")
                    },
                }
                continue

            raw = self._recv_packet_struct.parse(data)

            yield {
                "name": raw.name,
                "params": {k: v for k, v in raw.params.items() if not k.startswith("_")}  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                if isinstance(raw.params, Mapping)
                else raw.params,
            }

    @property
    def _state_protocol(self):
        return cast(
            MinecraftProtocolDefinition.MultiplayerStatePackets,
            getattr(self.protocol, self.state.value),
        )

    @property
    def _recv_packet_struct(self):
        if self.is_client:
            return self._state_protocol.toClient.packet

        return self._state_protocol.toServer.packet

    @property
    def _send_packet_struct(self):
        if self.is_client:
            return self._state_protocol.toServer.packet

        return self._state_protocol.toClient.packet

    def set_compression(self, threshold: int):
        """
        Set the compression threshold for this protocol. If `threshold` is a
        non-negative number, and the encoded packet's length exceeds `threshold` bytes,
        the packet is compressed with zlib, and any packets read follow a slightly
        different format. See the [Minecraft Wiki] for details.

        [Minecraft Wiki]: https://minecraft.wiki/w/Java_Edition_protocol/Packets#With_compression
        """

        self._compression_threshold = threshold
        self._decompression_handler.enabled = threshold >= 0

    def set_encryption(self, secret: bytes):
        """Sets the encryption key for this protocol. This cannot be undone."""

        if self._cipher is not None:
            raise RuntimeError("attempted to set encryption twice")

        self._cipher = Cipher(algorithms.AES(secret), modes.CFB8(secret))
        self._encryptor = self._cipher.encryptor()
        self._decryption_handler.cipher = self._cipher
        self._decryption_handler.decryptor = self._cipher.decryptor()

    def receive_bytes(self, data: bytes):
        """Put some received bytes into the protocol for processing."""

        return self._decryption_handler.receive_bytes(data)

    def received_packets(self) -> Generator[Packet[Any], None, None]:  # pyright: ignore[reportExplicitAny]
        """Generator to iterate through all packets currently available."""

        for packet in self._parse_more:
            if packet is None:
                break

            yield packet

    def send_packet(self, packet: Packet[Any] | bytes | bytearray) -> bytes:  # pyright: ignore[reportExplicitAny]
        """
        Processes the packet for sending. If `packet` is `bytes` or `bytearray`, it
        will be treated as raw packet data (not including the packet length), otherwise
        it will be serialized using the current state's packet.
        """

        if isinstance(packet, (bytes, bytearray)):
            data = packet
        else:
            try:
                # a packet is literally a typeddict doofus
                data = self._send_packet_struct.build(packet)  # pyright: ignore[reportArgumentType]
            except ConstructError as e:
                raise LocalProtocolError(f"could not serialize packet {packet}") from e

        if self._compression_threshold >= 0:  # if compression is enabled
            if (
                len(data) > self._compression_threshold
            ):  # and if our packet exceeds the threshold
                # compress it and prefix it with the packet's uncompressed length as a VarInt
                uncompressed_length = len(data)
                data = SizedVarInt(32).build(uncompressed_length) + zlib.compress(data)
            else:
                # else prefix a 0x00 to indicate that the packet is uncompressed
                data = b"\x00" + data

        data_length = len(data)

        if data_length > 2097151:  # 2 ** 21 - 1
            raise LocalProtocolError("packets cannot be larger than 2 ** 21 - 1 bytes")

        # frame the packet
        data = SizedVarInt(32, 3).build(len(data)) + data

        # encrypt the packet, if we have to
        if self._encryptor is not None:
            return self._encryptor.update(data)

        return data


class DecryptionHandler:
    """
    Minecraft packet decryption handler.

    https://minecraft.wiki/w/Java_Edition_protocol/Encryption
    """

    def __init__(self, decompression_handler: "DecompressionHandler | None" = None):
        self.cipher: Cipher[modes.CFB8] | None = None
        self.decryptor: CipherContext | None = None
        self._decompression_handler: DecompressionHandler = (
            decompression_handler or DecompressionHandler()
        )

    def set_encryption(self, secret: bytes):
        if self.cipher is not None:
            raise EncryptionSetTwiceError("attempted to set encryption twice")

        self.cipher = Cipher(algorithms.AES(secret), modes.CFB8(secret))
        self.decryptor = self.cipher.decryptor()

    def receive_bytes(self, data: bytes):
        if self.decryptor is not None:
            data = self.decryptor.update(data)

        return self._decompression_handler.receive_bytes(data)

    def process_buffer(self) -> bytes | None:
        return self._decompression_handler.process_buffer()


class DecompressionHandler:
    """
    Minecraft packet compression handler.

    https://minecraft.wiki/w/Java_Edition_protocol/Packets#Packet_format
    """

    def __init__(self, frame_decoder: "FrameDecoder | None" = None):
        self.enabled: bool = False
        self._frame_decoder: FrameDecoder = frame_decoder or FrameDecoder()

    def receive_bytes(self, data: bytes) -> None:
        return self._frame_decoder.receive_bytes(data)

    def process_buffer(self) -> bytes | None:
        if (packet := self._frame_decoder.process_buffer()) is None:
            return None

        if not self.enabled:
            return packet

        bio = io.BytesIO(packet)

        try:
            uncompressed_length = SizedVarInt(32).parse_stream(bio)
        except IntegerError:
            raise PacketParseError("invalid packet length")
        except StreamError:
            raise PacketParseError("packet too short")

        if uncompressed_length == 0:
            return bio.read()

        payload = zlib.decompress(bio.read())

        if len(payload) != uncompressed_length:
            raise PacketParseError("uncompressed size mismatch")

        return payload


class FrameDecoder:
    """
    Minecraft packet frame decoder.

    https://minecraft.wiki/w/Java_Edition_protocol/Packets#Packet_format

    Attributes:

    :attr buffer: The buffer to store incoming data while the frame is not complete.
    :attr recognize_legacy_ping: Whether to recognize pre-Netty server list ping.
        This should only be enabled on the server side during the handshaking stage.
    """

    def __init__(self):
        self.buffer: Buffer = Buffer()
        self.recognize_legacy_ping: bool = False
        self.packet_length: int | None = None

    def receive_bytes(self, data: bytes) -> None:
        self.buffer.feed(data)

    def process_buffer(self) -> bytes | None:
        if self.recognize_legacy_ping:
            if (payload := self.parse_legacy_server_ping()) is not None:
                return payload

            # parse_legacy_server_ping() may have mutated this.
            if self.recognize_legacy_ping:
                return None

        if self.packet_length is None:
            if (packet_length := self.parse_packet_length()) is None:
                return None

            self.packet_length = packet_length

        packet = self.buffer.consume_exactly(self.packet_length)

        if packet is None:
            return None

        self.buffer.commit()
        self.packet_length = None

        return packet

    # Dedicated support for this is implemented because
    # - It's a legacy protocol (aka it will never change)
    # - It's still popular (the official server still supports this)
    def parse_legacy_server_ping(self) -> bytes | None:
        if not self.recognize_legacy_ping:
            # The entrypoint that you're supposed to call, process_buffer(),
            # also guards on recognize_legacy_ping already.
            return None  # pragma: no cover

        maybe_ping = self.buffer.consume_at_most(2)
        consumed = len(maybe_ping)

        if not consumed:
            self.buffer.rollback()
            return None

        if maybe_ping[0] != 0xFE:
            # not a legacy ping, stop recognizing it, since this is supposed
            # to be the very first packet sent to the server
            self.recognize_legacy_ping = False
            self.buffer.rollback()
            return None

        if consumed == 1:  # beta 1.8 - 1.3.x ping
            self.buffer.commit()
            return maybe_ping

        # 1.4 - 1.5.x: FE 01
        # 1.6: FE 01 FA ...
        if maybe_ping[1] != 0x01:
            self.recognize_legacy_ping = False
            self.buffer.rollback()
            return None

        maybe_plugin_message_header = self.buffer.consume_at_most(1)
        consumed = len(maybe_plugin_message_header)

        # 1.4 - 1.5.x
        if not consumed or maybe_plugin_message_header[0] != 0xFA:
            # return the byte we thought to be the plugin message header,
            # but commit the FE 01
            self.buffer.return_bytes(consumed)
            self.buffer.commit()
            return maybe_ping

        query_name_length_bytes = self.buffer.consume_exactly(2)

        if query_name_length_bytes is None:
            # roll back to the very beginning, the 0xFE byte, while we wait
            # for more data to parse the packet
            self.buffer.rollback()
            return None

        query_name_length = Int16sb.parse(query_name_length_bytes)
        query_name_bytes = self.buffer.consume_exactly(
            query_name_length * 2
        )  # length is the number of utf-16be code points

        if query_name_bytes is None:
            # roll back to 0xFE while we wait for the message name to come in
            self.buffer.rollback()
            return None

        query_name = query_name_bytes.decode("utf-16be")

        if query_name != "MC|PingHost":
            # official server also does this, don't @ me
            self.recognize_legacy_ping = False
            self.buffer.rollback()
            return None

        data_length_bytes = self.buffer.consume_exactly(2)

        if data_length_bytes is None:
            self.buffer.rollback()
            return None

        data_length = Int16sb.parse(data_length_bytes)
        data_bytes = self.buffer.consume_exactly(data_length)

        if data_bytes is None:
            self.buffer.rollback()
            return None

        packet = self.buffer.consumed

        self.buffer.commit()
        return packet

    def parse_packet_length(self):
        bio = io.BytesIO(self.buffer.consume_at_most(3))
        consumed = len(bio.getvalue())

        if not consumed:
            self.buffer.rollback()
            return None

        try:
            packet_length = SizedVarInt(32, 3).parse_stream(bio)
        except IntegerError:
            raise PacketParseError("packet length cannot exceed 3 bytes") from None
        except StreamError:
            self.buffer.rollback()
            return None

        # packet length cannot be negative because we only use 21/32 bits

        self.buffer.return_bytes(consumed - bio.tell())
        self.buffer.commit()
        bio.close()

        return packet_length
