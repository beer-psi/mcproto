# pyright: reportAny=false, reportExplicitAny=false, reportMissingTypeArgument=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownVariableType=false
from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, override

from construct import Adapter, ConstructError

from .types import (
    NBTByte,
    NBTDouble,
    NBTFloat,
    NBTInt,
    NBTLong,
    NBTShort,
    NBTValue,
    TagID,
)

if TYPE_CHECKING:
    from construct import Context


class NBTAdapter(Adapter):
    """
    Adapter for converting the raw NBT output from Construct into nice
    Python types, and for converting nice Python types into raw forms for building.

    When decoding, the following translations are performed:

    | NBT            | Python                              |
    |----------------|-------------------------------------|
    | TAG_Byte       | :class:`mcproto.nbt.types.NBTByte`  |
    | TAG_Short      | :class:`mcproto.nbt.types.NBTShort` |
    | TAG_Int        | :class:`int`                        |
    | TAG_Long       | :class:`mcproto.nbt.types.NBTLong`  |
    | TAG_Float      | :class:`mcproto.nbt.types.NBTFloat` |
    | TAG_Double     | :class:`float`                      |
    | TAG_Byte_Array | :class:`bytes`                      |
    | TAG_String     | :class:`str`                        |
    | TAG_List       | :class:`list`                       |
    | TAG_Compound   | :class:`dict`                       |
    | TAG_Int_Array  | `list[int]`                         |
    | TAG_Long_Array | `list[mcproto.nbt.types.NBTLong]`   |

    When encoding, the following Python types are supported:

    | Python                                                 | NBT                                        |
    |--------------------------------------------------------|--------------------------------------------|
    | :class:`bool`                                          | TAG_Byte (0x01 if `True`, 0x00 if `False`) |
    | :class:`int`                                           | TAG_Int                                    |
    | :class:`float`                                         | TAG_Double                                 |
    | :class:`bytes`, :class:`bytearray`                     | TAG_Byte_Array                             |
    | :class:`str`                                           | TAG_String                                 |
    | `list[int]`                                            | TAG_Int_Array                              |
    | `list[mcproto.nbt.types.NBTLong]`                      | TAG_Long_Array                             |
    | :class:`collections.abc.Mapping` (e.g. :class:`dict`)  | TAG_Compound                               |
    | :class:`collections.abc.Iterable` (e.g. :class:`list`) | TAG_List                                   |

    In order to encode types not in this list (e.g. byte and short), use the value
    wrapper classes as shown in the decoding table.

    The root tag's name will always be removed. If the root tag's name is necessary, use raw decoding
    to obtain it, and then use :func:`mcproto.nbt.to_builtins` to convert to Python objects.

    Heterogenous (mixed-type) lists are encoded as a list of compounds, each having a single empty key paired
    with the value. For example, `[1, "abc"]` becomes `[{"": 1}, {"": "abc"}]`. These compounds are unwrapped
    automatically on decoding, provided that all items in the list are of this form.

    ```python
    >>> NBTAdapter(Pass)._encode([1, "abc"], {}, "")
    {
        'type': <TagID.LIST: 9>,
        'name': '',
        'value': {
            'type': <TagID.COMPOUND: 10>,
            'items': [
                [{'type': <TagID.INT: 3>, 'name': '', 'value': 1}, {'type': <TagID.END: 0>, 'name': None, 'value': None}],
                [{'type': <TagID.STRING: 8>, 'name': '', 'value': 'abc'}, {'type': <TagID.END: 0>, 'name': None, 'value': None}],
            ],
        },
    }
    >>> NBTAdapter(Pass)._decode(_, {}, "")
    [1, 'abc']
    ```

    To explicitly specify the tag you want, you can pass raw NBT data. Raw NBT data is a dictionary with
    exactly 3 keys:
    - `type` (:class:`mcproto.nbt.types.TagID`)
    - `name` (:class:`str`)
    - `value` (depends on `type`)

    Raw NBT data will be passed through to the serializer untouched.

    For example, to create a TAG_List of TAG_Int (instead of TAG_Int_Array):

    ```python
    {
        "listTest": {
            "type": TagID.LIST,
            "name": "listTest",
            "value": {
                "type": TagID.INT,
                "items": [11, 12, 13, 14, 15],
            },
        },
    }
    ```
    """

    @override
    def _encode(self, obj: object, context: "Context", path: str) -> Any:
        if isinstance(obj, bool):
            return {
                "type": TagID.BYTE,
                "name": "",
                "value": b"\x01" if obj else b"\x00",
            }
        if isinstance(obj, int):
            return {"type": TagID.INT, "name": "", "value": obj}
        if isinstance(obj, float):
            return {"type": TagID.DOUBLE, "name": "", "value": obj}
        if isinstance(obj, (bytes, bytearray)):
            return {"type": TagID.BYTE_ARRAY, "name": "", "value": bytes(obj)}
        if isinstance(obj, str):
            return {"type": TagID.STRING, "name": "", "value": obj}
        if isinstance(obj, NBTValue):
            return {"type": obj.TAG, "name": "", "value": obj.value}
        if isinstance(obj, Mapping):
            # allow dicts with exactly 3 keys `type`, `name`, `value` to pass through
            # in case we need to account for some really stupid edge case
            if (
                len(obj.keys()) == 3
                and sorted(obj.keys()) == ["name", "type", "value"]
                and isinstance(obj["type"], TagID)
                and isinstance(obj["name"], str)
            ):
                return obj

            compound_items: list[object] = []

            for k, v in obj.items():
                v = self._encode(v, context, f"{path} -> {k}")
                v["name"] = k

                compound_items.append(v)

            compound_items.append({"type": TagID.END, "name": None, "value": None})

            return {"type": TagID.COMPOUND, "name": "", "value": compound_items}
        if isinstance(obj, Iterable):
            items = [
                self._encode(item, context, f"{path}[{i}]")
                for i, item in enumerate(obj)
            ]
            item_types = {item["type"] for item in items}

            # a heterogenous list is stored as a list of NBT compounds
            if len(item_types) != 1:
                return {
                    "type": TagID.LIST,
                    "name": "",
                    "value": {
                        "type": TagID.COMPOUND,
                        "items": [
                            [
                                {
                                    "type": item["type"],
                                    "name": "",
                                    "value": item["value"],
                                },
                                {"type": TagID.END, "name": None, "value": None},
                            ]
                            for item in items
                        ],
                    },
                }

            item_type = item_types.pop()
            item_values = [item["value"] for item in items]

            # specializations
            if item_type == TagID.INT:
                return {"type": TagID.INT_ARRAY, "name": "", "value": item_values}
            if item_type == TagID.LONG:
                return {"type": TagID.LONG_ARRAY, "name": "", "value": item_values}

            return {
                "type": TagID.LIST,
                "name": "",
                "value": {"type": item_type, "items": item_values},
            }

        raise TypeError(
            f"object of type {obj.__class__.__name__} cannot be serialized into NBT"
        )

    @override
    def _decode(self, obj: "Mapping[Any, Any]", context: "Context", path: str) -> Any:
        ty = obj["type"]
        value = obj["value"]

        if ty == TagID.END:
            raise ConstructError("unexpected end tag outside of a container", path)
        if ty == TagID.BYTE:
            return NBTByte(value)
        if ty == TagID.SHORT:
            return NBTShort(value)
        if ty == TagID.INT:
            return NBTInt(value)
        if ty == TagID.LONG:
            return NBTLong(value)
        if ty == TagID.FLOAT:
            return NBTFloat(value)
        if ty == TagID.DOUBLE:
            return NBTDouble(value)
        if ty == TagID.BYTE_ARRAY:
            return value  # already bytes
        if ty == TagID.STRING:
            return value  # already string
        if ty == TagID.LIST:
            items: list[object] = []
            item_type = value["type"]

            # a heterogenous list is serialized as a list of compounds
            heterogenous_list = item_type == TagID.COMPOUND and all(
                len(item) == 2 and not item[0]["name"] for item in value["items"]
            )

            for item in value["items"]:
                decoded = self._decode(
                    {"type": item_type, "name": "", "value": item}, context, path
                )

                if heterogenous_list:
                    items.append(next(iter(decoded.values())))
                else:
                    items.append(decoded)

            return items
        if ty == TagID.COMPOUND:
            compound: dict[str, object] = {}

            for tag in value:
                if tag["type"] == TagID.END:
                    break

                compound[tag["name"]] = self._decode(tag, context, path)

            return compound
        if ty == TagID.INT_ARRAY:
            return value  # already a list of ints
        if ty == TagID.LONG_ARRAY:
            return [NBTLong(v) for v in value]

        raise ConstructError(f"unknown type tag for {obj}: {ty}", path)
