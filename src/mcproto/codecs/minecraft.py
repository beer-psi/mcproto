# pyright: reportAttributeAccessIssue=false, reportMissingTypeArgument=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownVariableType=false
import os
from collections.abc import Iterable, Sequence
from typing import IO, TYPE_CHECKING, TypedDict

from construct import (
    Array,
    Construct,
    ConstructError,
    ExprAdapter,
    If,
    Int8ub,
    ListContainer,
    Struct,
    obj_,
    stream_read,
    stream_seek,
    stream_tell,
    stream_write,
    this,
)
from protodef.converter.context import ConverterContext
from protodef.datatypes.varint import SizedVarInt

if TYPE_CHECKING:
    from construct import Context


class EntityMetadataLoop(Construct):
    def __init__(self, end_val: int, subcon: Construct):
        super().__init__()
        self.end_val: int = end_val
        self.subcon: Construct = subcon

    def _parse(self, stream: IO[bytes], context: "Context", path: str):
        result = ListContainer()

        while True:
            index = Int8ub._parse(stream, context, path)

            if index == self.end_val:
                return result

            _ = stream_seek(stream, -1, os.SEEK_CUR, path)
            result.append(self.subcon._parse(stream, context, path))

    def _build(self, obj: object, stream: IO[bytes], context: "Context", path: str):
        if not isinstance(obj, Iterable):
            msg = f"entity data must be iterable, got {obj}"
            raise ConstructError(msg, path)

        for entry in obj:
            self.subcon._build(entry, stream, context, path)

        stream_write(stream, bytes([self.end_val]), 1, path)

        return obj


class EntityMetadataLoopArguments(TypedDict):
    endVal: int
    type: str | tuple[str, object]


def convert_entity_metadata_loop(
    ctx: ConverterContext, arg: EntityMetadataLoopArguments
):
    return EntityMetadataLoop(arg["endVal"], ctx.convert_type(arg["type"]))


class TopBitSetTerminatedArray(Construct):
    def __init__(self, subcon: Construct):
        super().__init__()
        self.subcon: Construct = subcon

    def _parse(self, stream: IO[bytes], context: "Context", path: str):
        result = ListContainer()

        while True:
            b = Int8ub._parse(stream, context, path)

            _ = stream_seek(stream, -1, os.SEEK_CUR, path)
            stream_write(stream, bytes([b & 0x7F]), 1, path)
            _ = stream_seek(stream, -1, os.SEEK_CUR, path)

            result.append(self.subcon._parse(stream, context, path))

            if (b & 0x80) == 0:
                return result

    def _build(self, obj: object, stream: IO[bytes], context: "Context", path: str):
        if not isinstance(obj, Sequence):
            msg = f"array data must be sequence, got {obj}"
            raise ConstructError(msg, path)

        for i, item in enumerate(obj):
            prev_pos = stream_tell(stream, path)

            self.subcon._build(item, stream, context, path)

            new_pos = stream_tell(stream, path)

            if i != len(obj) - 1:
                # jump to the first byte written and set the top bit if there's more
                _ = stream_seek(stream, prev_pos, os.SEEK_SET, path)

                b = stream_read(stream, 1, path)[0]

                _ = stream_seek(stream, -1, os.SEEK_CUR, path)
                stream_write(stream, bytes([b | 0x80]), 1, path)
                _ = stream_seek(stream, new_pos, os.SEEK_SET, path)


class TopBitSetTerminatedArrayArguments(TypedDict):
    type: str | tuple[str, object]


def convert_top_bit_set_terminated_array(
    ctx: ConverterContext, arg: TopBitSetTerminatedArrayArguments
):
    return TopBitSetTerminatedArray(ctx.convert_type(arg["type"]))


class RegistryEntryHolderType(TypedDict):
    name: str
    type: str | tuple[str, object]


class RegistryEntryHolderArguments(TypedDict):
    baseName: str
    otherwise: RegistryEntryHolderType


def convert_registry_entry_holder(
    ctx: ConverterContext, arg: RegistryEntryHolderArguments
):
    base_name = arg["baseName"]
    otherwise_name = arg["otherwise"]["name"]
    otherwise_type = ctx.convert_type(arg["otherwise"]["type"])

    return Struct(
        base_name / ExprAdapter(SizedVarInt(32), obj_ - 1, obj_ + 1),
        otherwise_name / If(this[base_name] == -1, otherwise_type),
    )


class RegistryEntryHolderSetArguments(TypedDict):
    base: RegistryEntryHolderType
    otherwise: RegistryEntryHolderType


def convert_registry_entry_holder_set(
    ctx: ConverterContext, arg: RegistryEntryHolderSetArguments
):
    base_name = arg["base"]["name"]
    base_type = ctx.convert_type(arg["base"]["type"])
    otherwise_name = arg["otherwise"]["name"]
    otherwise_type = ctx.convert_type(arg["otherwise"]["type"])

    return Struct(
        "type" / SizedVarInt(32),
        base_name / If(this.type == 0, base_type),
        otherwise_name / If(this.type != 0, Array(this.type - 1, otherwise_type)),
    )
