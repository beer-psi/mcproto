import random
import zlib

import pytest

from mcproto.exceptions import EncryptionSetTwiceError, PacketParseError
from mcproto.protocol import DecompressionHandler, DecryptionHandler, FrameDecoder

MINECRAFT_1_6_SERVER_LIST_PING = bytes.fromhex(
    "fe01fa000b004d0043007c00500069006e00670048006f007300740019490009006c006f00630061006c0068006f00730074000063dd"
)


def test_frame_decoder_nothing_in_nothing_out():
    frame_decoder = FrameDecoder()

    assert frame_decoder.process_buffer() is None

    frame_decoder.recognize_legacy_ping = True
    assert frame_decoder.process_buffer() is None


def test_frame_decoder_splits_packets():
    frame_decoder = FrameDecoder()

    frame_decoder.receive_data(
        b"\x06"  # first packet's length
        + b"\x01\x02\x03\x04\x05\x06"  # first packet's content
        + b"\xff"  # second packet's length, incomplete varint
    )
    assert frame_decoder.process_buffer() == b"\x01\x02\x03\x04\x05\x06"
    assert frame_decoder.process_buffer() is None
    assert frame_decoder.buffer.buffer == b"\xff"


def test_frame_decoder_can_handle_length_and_content_split():
    frame_decoder = FrameDecoder()

    frame_decoder.receive_data(b"\xff")
    assert frame_decoder.process_buffer() is None
    assert frame_decoder.buffer.buffer == b"\xff"

    frame_decoder.receive_data(b"\x01")
    assert frame_decoder.process_buffer() is None  # it has consumed the packet length
    assert frame_decoder.packet_length == 255
    assert frame_decoder.buffer.buffer == b""

    frame_decoder.receive_data(bytes(128))
    assert frame_decoder.process_buffer() is None
    assert frame_decoder.buffer.buffer == bytes(128)

    frame_decoder.receive_data(bytes(127))
    assert frame_decoder.process_buffer() == bytes(255)


def test_frame_decoder_splits_multiple_packets():
    frame_decoder = FrameDecoder()

    for _ in range(10):
        length = random.randrange(1, 64)
        frame_decoder.receive_data(length.to_bytes(1, "little"))
        frame_decoder.receive_data(bytes(length))

    for _ in range(10):
        assert frame_decoder.process_buffer() is not None

    assert frame_decoder.process_buffer() is None
    assert frame_decoder.buffer.buffer == b""


@pytest.mark.parametrize(
    "data",
    [b"\xfe", b"\xfe\x01", MINECRAFT_1_6_SERVER_LIST_PING],
)
def test_frame_decoder_recognizes_legacy_server_ping(data: bytes):
    frame_decoder = FrameDecoder()
    frame_decoder.recognize_legacy_ping = True

    frame_decoder.receive_data(data)
    assert frame_decoder.process_buffer() == data


@pytest.mark.parametrize(
    "data",
    [
        b"\xff",
        b"\xfe\x02",
        # same 1.6 payload as above, but now it's NC|PingHost
        bytes.fromhex(
            "fe01fa000b004e0043007c00500069006e00670048006f007300740019490009006c006f00630061006c0068006f00730074000063dd"
        ),
    ],
)
def test_recognize_legacy_ping_disables_on_invalid_packets(data: bytes):
    frame_decoder = FrameDecoder()
    frame_decoder.recognize_legacy_ping = True

    frame_decoder.receive_data(data)
    _ = frame_decoder.process_buffer()
    assert not frame_decoder.recognize_legacy_ping


def test_recognize_split_legacy_ping():
    frame_decoder = FrameDecoder()
    frame_decoder.recognize_legacy_ping = True

    frame_decoder.receive_data(MINECRAFT_1_6_SERVER_LIST_PING[:3])
    assert frame_decoder.process_buffer() is None
    assert frame_decoder.recognize_legacy_ping
    assert frame_decoder.buffer.buffer == b"\xfe\x01\xfa"

    for i in range(3, len(MINECRAFT_1_6_SERVER_LIST_PING) - 1):
        frame_decoder.receive_data(MINECRAFT_1_6_SERVER_LIST_PING[i].to_bytes(1))
        assert frame_decoder.process_buffer() is None
        assert frame_decoder.recognize_legacy_ping
        assert frame_decoder.buffer.buffer == MINECRAFT_1_6_SERVER_LIST_PING[: i + 1]

    frame_decoder.receive_data(MINECRAFT_1_6_SERVER_LIST_PING[-1].to_bytes(1))
    assert frame_decoder.process_buffer() == MINECRAFT_1_6_SERVER_LIST_PING


def test_bad_packet_length():
    frame_decoder = FrameDecoder()

    frame_decoder.receive_data(b"\xff\xff\xff")

    with pytest.raises(PacketParseError):
        _ = frame_decoder.process_buffer()


def test_max_packet_length():
    frame_decoder = FrameDecoder()

    frame_decoder.receive_data(b"\xff\xff\x7f")
    _ = frame_decoder.process_buffer()

    assert frame_decoder.packet_length == 2**21 - 1


def test_decompression_handler_returns_none_on_incomplete_frame():
    decompression_handler = DecompressionHandler(FrameDecoder())

    decompression_handler.receive_data(b"\x06\x01\x02\x03\x04\x05")
    assert decompression_handler.process_buffer() is None


def test_decompression_handler_do_nothing_if_disabled():
    decompression_handler = DecompressionHandler(FrameDecoder())

    decompression_handler.receive_data(b"\x06\x01\x02\x03\x04\x05\x06")
    assert decompression_handler.process_buffer() == b"\x01\x02\x03\x04\x05\x06"


def test_decompression_handler_uncompressed():
    decompression_handler = DecompressionHandler(FrameDecoder())
    decompression_handler.enabled = True

    decompression_handler.receive_data(b"\x07\x00\x01\x02\x03\x04\x05\x06")
    assert decompression_handler.process_buffer() == b"\x01\x02\x03\x04\x05\x06"


def test_decompression_handler_compressed():
    decompression_handler = DecompressionHandler(FrameDecoder())
    decompression_handler.enabled = True

    data = b"\x06" + zlib.compress(b"\x01\x02\x03\x04\x05\x06")

    decompression_handler.receive_data(len(data).to_bytes(1))
    decompression_handler.receive_data(data)
    assert decompression_handler.process_buffer() == b"\x01\x02\x03\x04\x05\x06"


def test_decompression_handler_truncated_uncompressed_length():
    decompression_handler = DecompressionHandler(FrameDecoder())
    decompression_handler.enabled = True

    decompression_handler.receive_data(b"\x01\xff")

    with pytest.raises(PacketParseError):
        _ = decompression_handler.process_buffer()


def test_decompression_handler_uncompressed_length_too_large():
    decompression_handler = DecompressionHandler(FrameDecoder())
    decompression_handler.enabled = True

    decompression_handler.receive_data(b"\x05\xff\xff\xff\xff\xff")

    with pytest.raises(PacketParseError):
        _ = decompression_handler.process_buffer()


def test_decompression_handler_uncompressed_length_mismatch():
    decompression_handler = DecompressionHandler(FrameDecoder())
    decompression_handler.enabled = True

    data = b"\x07" + zlib.compress(b"\x01\x02\x03\x04\x05\x06")

    decompression_handler.receive_data(len(data).to_bytes(1))
    decompression_handler.receive_data(data)

    with pytest.raises(PacketParseError):
        _ = decompression_handler.process_buffer()


def test_decryption_handler_do_nothing_if_disabled():
    decryption_handler = DecryptionHandler(DecompressionHandler(FrameDecoder()))

    decryption_handler.receive_data(b"\x01\x00")
    assert decryption_handler.process_buffer() == b"\x00"


def test_decryption_handler_decrypts_data():
    decryption_handler = DecryptionHandler(DecompressionHandler(FrameDecoder()))
    decryption_handler.set_encryption(b"S3cur3P455w0rd!!")

    decryption_handler.receive_data(b"\xb2\x4b")
    assert decryption_handler.process_buffer() == b"\x00"

    # The decryptor should continue using the same cipher context as before.
    decryption_handler.receive_data(b"\xa3\x25")
    assert decryption_handler.process_buffer() == b"\x00"


def test_decryption_handler_set_twice():
    decryption_handler = DecryptionHandler(DecompressionHandler(FrameDecoder()))
    decryption_handler.set_encryption(b"S3cur3P455w0rd!!")

    with pytest.raises(EncryptionSetTwiceError):
        decryption_handler.set_encryption(b"S3cur3P455w0rd!!")
