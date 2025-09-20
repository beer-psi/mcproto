# pyright: reportAny=false, reportArgumentType=false, reportExplicitAny=false, reportMissingTypeArgument=false, reportUnknownArgumentType=false, reportUnknownVariableType=false
from enum import IntEnum
from typing import IO, TYPE_CHECKING, Any

from construct import (
    Construct,
    Enum,
    ExplicitError,
    ExprAdapter,
    Float32b,
    Float32l,
    Float64b,
    Float64l,
    GreedyBytes,
    If,
    Int8sb,
    Int16sb,
    Int16sl,
    Int16ub,
    Int16ul,
    Int32sb,
    Int32sl,
    Int64sb,
    Int64sl,
    LazyBound,
    Pass,
    Prefixed,
    PrefixedArray,
    RepeatUntil,
    Struct,
    Switch,
    evaluate,
    this,
)
from mutf8 import decode_modified_utf8, encode_modified_utf8
from protodef.datatypes.varint import SizedVarInt, SizedZigZag

from .types import TagID

if TYPE_CHECKING:
    from construct import ConstantOrContextLambda, Context


class DetailedError(Construct):
    def __init__(self, msgfunc: "ConstantOrContextLambda[str]"):
        super().__init__()
        self.msgfunc: "ConstantOrContextLambda[str]" = msgfunc

    def _parse(self, _stream: IO[bytes], context: "Context", path: str):
        raise ExplicitError(evaluate(self.msgfunc, context), path=path)

    def _build(self, _obj: object, _stream: IO[bytes], context: "Context", path: str):
        raise ExplicitError(evaluate(self.msgfunc, context), path=path)


class NativeEnum(Enum):
    def __init__(self, subcon: "Construct[Any, Any]", enum: type[IntEnum]):
        super().__init__(subcon)

        self.encmapping.clear()
        self.decmapping.clear()

        for enum_item in enum:
            self.encmapping[enum_item] = enum_item.value
            self.encmapping[enum_item.name] = enum_item.value
            self.encmapping[enum_item.value] = enum_item.value

            self.decmapping[enum_item.value] = enum_item


UnknownEncodingError = DetailedError(
    lambda ctx: f"unknown NBT encoding {ctx._params.nbt_encoding!r}"
)
Int16 = Switch(
    this._params.nbt_encoding,
    {
        "big": Int16sb,
        "little": Int16sl,
        "little-varint": Int16sl,
    },
    UnknownEncodingError,
)
Int32 = Switch(
    this._params.nbt_encoding,
    {
        "big": Int32sb,
        "little": Int32sl,
        "little-varint": SizedZigZag(32),
    },
    UnknownEncodingError,
)
Int64 = Switch(
    this._params.nbt_encoding,
    {
        "big": Int64sb,
        "little": Int64sl,
        "little-varint": SizedZigZag(64),
    },
    UnknownEncodingError,
)
Float32 = Switch(
    this._params.nbt_encoding,
    {
        "big": Float32b,
        "little": Float32l,
        "little-varint": Float32l,
    },
    UnknownEncodingError,
)
Float64 = Switch(
    this._params.nbt_encoding,
    {
        "big": Float64b,
        "little": Float64l,
        "little-varint": Float64l,
    },
    UnknownEncodingError,
)
StringLength = Switch(
    this._params.nbt_encoding,
    {
        "big": Int16ub,
        "little": Int16ul,
        "little-varint": SizedVarInt(32),
    },
    UnknownEncodingError,
)

# XXX: Does Bedrock also use the fucked-up JVM UTF-8 encoding?
ShortString = ExprAdapter(
    Prefixed(StringLength, GreedyBytes),
    lambda data, ctx: decode_modified_utf8(data),
    lambda value, ctx: encode_modified_utf8(value),
)


def TagValue(keyfunc: "ConstantOrContextLambda[Any]"):
    return Switch(
        keyfunc,
        {
            TagID.END: Pass,
            TagID.BYTE: Int8sb,  # endianness doesn't matter for a single byte
            TagID.SHORT: Int16,
            TagID.INT: Int32,
            TagID.LONG: Int64,
            TagID.FLOAT: Float32,
            TagID.DOUBLE: Float64,
            TagID.BYTE_ARRAY: Prefixed(Int32, GreedyBytes),
            TagID.STRING: ShortString,
            TagID.LIST: Struct(
                "type" / NativeEnum(Int8sb, TagID),
                "items"
                / PrefixedArray(Int32, LazyBound(lambda: TagValue(this._.type))),
            ),
            TagID.COMPOUND: RepeatUntil(
                lambda x, ls, ctx: x["type"] == TagID.END, LazyBound(lambda: Tag)
            ),
            TagID.INT_ARRAY: PrefixedArray(
                Int32,
                Switch(
                    this._params.nbt_encoding,
                    {"big": Int32sb, "little": Int32sl, "little-varint": Int32sl},
                    UnknownEncodingError,
                ),
            ),
            TagID.LONG_ARRAY: PrefixedArray(
                Int32,
                Switch(
                    this._params.nbt_encoding,
                    {"big": Int64sb, "little": Int64sl, "little-varint": Int64sl},
                    UnknownEncodingError,
                ),
            ),
        },
        DetailedError(lambda ctx: f"unknown NBT tag {evaluate(keyfunc, ctx)}"),
    )


Tag = Struct(
    "type" / NativeEnum(Int8sb, TagID),
    "name" / If(lambda ctx: ctx["type"] != TagID.END, ShortString),
    "value" / TagValue(this.type),
)
AnonymousTag = Struct(
    "type" / NativeEnum(Int8sb, TagID),
    "value" / TagValue(this.type),
)
