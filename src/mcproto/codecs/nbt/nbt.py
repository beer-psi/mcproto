# pyright: reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false
import gzip
import io
import os
from typing import IO, Any, Literal

from construct import Adapter, ConstructError, Container, Struct
from typing_extensions import Buffer

from .adapter import NBTAdapter
from .structs import AnonymousTag, Tag

_LoadEncoding = Literal["big", "little", "little-varint", "auto"]
_DumpEncoding = Literal["big", "little", "little-varint"]


def _load(
    fp: IO[bytes],
    encoding: _LoadEncoding,
    *,
    tag_construct: Struct,
    nbt_adapter: type["Adapter[Any, Any, Any, Any]"] | None = None,
):
    if nbt_adapter is not None:
        tag_construct = nbt_adapter(tag_construct)  # pyright: ignore[reportAssignmentType]

    if not isinstance(fp.read(0), bytes):
        raise ValueError("File must be in binary mode")

    if encoding == "auto" and not fp.seekable():
        raise ValueError("File must be seekable when using 'auto' encoding")

    if encoding == "auto":
        exc: ConstructError | UnicodeDecodeError | None = None

        for encoding in ("big", "little", "little-varint"):
            try:
                return tag_construct.parse_stream(fp, nbt_encoding=encoding)
            except (ConstructError, UnicodeDecodeError) as e:
                # store the big-endian exception
                if exc is None:
                    exc = e
                _ = fp.seek(0, os.SEEK_SET)

        assert exc is not None

        if isinstance(exc, UnicodeDecodeError):
            raise exc

        raise ValueError("Invalid NBT data") from exc

    try:
        return tag_construct.parse_stream(fp, nbt_encoding=encoding)
    except ConstructError as e:
        raise ValueError("Invalid NBT data") from e


def load(
    fp: IO[bytes],
    encoding: _LoadEncoding = "auto",
    *,
    raw: bool = False,
    anonymous: bool = False,
) -> Any:
    """
    Deserializes NBT file object `fp` to a Python object. This does not automatically
    decompress the data. If the file is compressed, open it using :class:`gzip.GzipFile`.

    Parameters:
    :param fp: a `.read()` supporting binary file containing the NBT data
        to be deserialized.
    :param encoding: The encoding of the NBT data. If `auto` is used, the function
        attempts to parse using all encodings and returns the first successful one.
        As a result, `fp` must support seeking when using `auto`.
    :param bool raw: Whether to return the raw NBT representation (a series of `type`,
        `name`, `value` dictionaries) instead of a simplified Python representation.
    :param bool anonymous: Whether the NBT's root tag's name has been omitted.
    :type fp: file-like object
    :type encoding: "big", "little", "little-varint" or "auto"
    :rtype: Any
    :raises ValueError: When the data being deserialized is not valid NBT data, or
        the file object is not binary, or the file object is not seekable when
        using `encoding=auto`.
    :raises UnicodeDecodeError: When NBT strings have invalid UTF-8 data.
    """
    return _load(
        fp,
        encoding,
        tag_construct=AnonymousTag if anonymous else Tag,
        nbt_adapter=None if raw else NBTAdapter,
    )


def loads(
    b: Buffer,
    encoding: _LoadEncoding = "auto",
    *,
    raw: bool = False,
    anonymous: bool = False,
) -> Any:
    """
    Deserializes `b` (a buffer, such as :class:`bytes` or :class:`bytearray`) containing
    NBT data to a Python object. `b` can be gzip-compressed, in which case it will
    automatically be decompressed.

    Parameters have the same meaning as :func:`load`.
    """
    fp = io.BytesIO(b)
    magic = fp.read(2)
    _ = fp.seek(0, os.SEEK_SET)

    if magic == b"\x1f\x8b":
        fp = gzip.GzipFile(fileobj=fp)

    return _load(
        fp,  # pyright: ignore[reportArgumentType]
        encoding,
        tag_construct=AnonymousTag if anonymous else Tag,
        nbt_adapter=None if raw else NBTAdapter,
    )


def _dump(
    obj: Any,
    fp: IO[bytes],
    encoding: _DumpEncoding = "big",
    *,
    tag_construct: Struct,
    nbt_adapter: type["Adapter[Any, Any, Any, Any]"] | None = None,
    compress: bool = True,
):
    if nbt_adapter is not None:
        tag_construct = nbt_adapter(tag_construct)  # pyright: ignore[reportAssignmentType]

    if compress:
        fp = gzip.GzipFile(mode="w", fileobj=fp)  # pyright: ignore[reportAssignmentType]

    try:
        tag_construct.build_stream(obj, fp, nbt_encoding=encoding)
    except ConstructError as e:
        raise ValueError("Could not serialize into NBT data") from e


def dump(
    obj: Any,
    fp: IO[bytes],
    encoding: _DumpEncoding = "big",
    *,
    raw: bool = False,
    compress: bool = True,
    anonymous: bool = False,
) -> None:
    """
    Serialize `obj` as NBT to write-supporting binary mode file-like object `fp`.

    Parameters:
    :param Any obj: The data to serialize into NBT.
    :param fp: The file-like object `obj` will be serialized to. `fp.write()` must
        support :class:`bytes` input.
    :param encoding: The encoding of the NBT data. Java uses big-endian (`big`),
        while Bedrock uses little-endian (`little`) encoding. `little-varint` is a
        modified version of `little` that uses variable-length integers (VarInts)
        for integers and longs.
    :param bool raw: Whether the data being serialized is a raw NBT representation
        (a series of `type`, `name`, `value` dictionaries) instead of a simplified
        Python representation. When `raw` is `False`, dictionaries with exactly
        3 items: `type` (:class:`mcproto.nbt.structs.TagID`), `name` (:class:`str`)
        and `value` are still interpreted as raw representation.
    :param bool compress: Whether to compress the serialized data with :mod:`gzip`.
    :param bool anonymous: Whether to serialize NBT with the root tag's name omitted.
    :type fp: file-like object
    :type encoding: "big", "little", "little-varint"
    :raises ValueError: if the data could not be serialized into NBT.
    """

    _dump(
        obj,
        fp,
        encoding,
        tag_construct=AnonymousTag if anonymous else Tag,
        nbt_adapter=None if raw else NBTAdapter,
        compress=compress,
    )


def dumps(
    obj: Any,
    encoding: _DumpEncoding = "big",
    *,
    raw: bool = False,
    compress: bool = True,
    anonymous: bool = False,
) -> bytes:
    """
    Serialize `obj` to a buffer containing NBT data.

    Parameters have the same meaning as :func:`dump`.
    """
    bio = io.BytesIO()

    _dump(
        obj,
        bio,
        encoding,
        tag_construct=AnonymousTag if anonymous else Tag,
        nbt_adapter=None if raw else NBTAdapter,
        compress=compress,
    )

    return bio.getvalue()


def to_builtins(data: Any) -> Any:
    """
    Convert raw NBT representations. to one composed of mostly builtin types.
    Numeric types (except TAG_Int and TAG_Double) are still wrapped in
    a simple dataclass.

    ```python
    >>> nbt.to_builtins(
        {
            "type": TagID.COMPOUND,
            "name": "hello world",
            "value": [
                {"type": TagID.STRING, "name": "name", "value": "Bananrama"},
                {"type": TagID.SHORT, "name": "shortTest", "value": 32767},
                {"type": TagID.INT, "name": "intTest", "value": 2147483647},
                {"type": TagID.END, "name": None, "value": None},
            ],
        },
    )
    {'name': 'Bananrama', 'shortTest': 32767s, 'intTest': 2147483647}
    ```
    """
    return NBTAdapter(Tag)._decode(data, Container(), "")  # pyright: ignore[reportArgumentType, reportPrivateUsage]


def to_raw(data: Any) -> Any:
    """
    Convert builtin types to the raw NBT representation.

    ```python
    >>> nbt.to_raw({'name': 'Bananrama', 'shortTest': NBTShort(32767), 'intTest': 2147483647})
    {
        'type': <TagID.COMPOUND: 10>,
        'name': '',
        'value': [
            {'type': <TagID.STRING: 8>, 'name': 'name', 'value': 'Bananrama'},
            {'type': <TagID.SHORT: 2>, 'name': 'shortTest', 'value': 32767},
            {'type': <TagID.INT: 3>, 'name': 'intTest', 'value': 2147483647},
            {'type': <TagID.END: 0>, 'name': None, 'value': None},
        ],
    }
    ```
    """
    return NBTAdapter(Tag)._encode(data, Container(), "")  # pyright: ignore[reportArgumentType, reportPrivateUsage]
