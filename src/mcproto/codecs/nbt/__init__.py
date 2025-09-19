"""
Named Binary Tag (NBT) parsing tools.

From the initial specification:
```
NBT (Named Binary Tag) is a tag based binary format designed to carry large
amounts of binary data with smaller amounts of additional data.
An NBT file consists of a single GZIPped Named Tag of type TAG_Compound.
```

The original official specification can be found on the [Internet Archive](https://web.archive.org/web/20110723210920/http://www.minecraft.net/docs/NBT.txt).
An up-to-date reference can be found at the [Minecraft Wiki](https://minecraft.wiki/w/NBT_format).

## Encoding

There are currently multiple NBT encodings in use:
- Minecraft Java uses big-endian numbers.
- Minecraft Bedrock uses little-endian numbers.
- When serializing NBTs to send over the network, Minecraft Bedrock uses
variable-length integers for i32 and i64, as well as string lengths.

These encodings are exposed in the API as `big`, `little` and `little-varint` respectively.

Additionally, since Java 1.20.2, when sending NBT over the network, the root tag's name
is removed.
"""

from .nbt import (
    dump,
    dumps,
    load,
    loads,
    to_builtins,
    to_raw,
)

__all__ = (
    "dump",
    "dumps",
    "load",
    "loads",
    "to_builtins",
    "to_raw",
)
