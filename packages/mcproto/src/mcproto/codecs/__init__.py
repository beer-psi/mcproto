# pyright: reportAny=false, reportUnknownArgumentType=false
from typing import Final

from construct import (
    Flag,
    FocusedSeq,
    GreedyBytes,
    If,
    Rebuild,
    this,
)
from protodef.datatypes import SizedVarInt

from .context import ContextParamsProvider
from .minecraft import (
    convert_entity_metadata_loop,
    convert_registry_entry_holder,
    convert_registry_entry_holder_set,
    convert_top_bit_set_terminated_array,
)
from .nbt.adapter import NBTAdapter
from .nbt.structs import AnonymousTag, Tag
from .uuid import UUID

NBT = ContextParamsProvider(NBTAdapter(Tag), nbt_encoding="big")
AnonymousNBT = ContextParamsProvider(NBTAdapter(AnonymousTag), nbt_encoding="big")

ADDITIONAL_PROTODEF_TYPES: Final = {
    "entityMetadataLoop": convert_entity_metadata_loop,
    "registryEntryHolder": convert_registry_entry_holder,
    "registryEntryHolderSet": convert_registry_entry_holder_set,
    "topBitSetTerminatedArray": convert_top_bit_set_terminated_array,
    "UUID": UUID,
    "nbt": NBT,
    "optionalNbt": FocusedSeq(
        "value",
        "exists" / Rebuild(Flag, lambda ctx: ctx.value is not None),
        "value" / If(this.exists, NBT),
    ),
    "anonymousNbt": AnonymousNBT,
    "anonOptionalNbt": FocusedSeq(
        "value",
        "exists" / Rebuild(Flag, lambda ctx: ctx.value is not None),
        "value" / If(this.exists, AnonymousNBT),
    ),
    "varlong": SizedVarInt(32),
    "restBuffer": GreedyBytes,
}
