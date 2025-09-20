# pyright: reportAny=false, reportUninitializedInstanceVariable=false
import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Literal,
    TypedDict,
    TypeVar,
    overload,
)

from .types.attributes import Attribute
from .types.biomes import Biome
from .types.block_collision_shapes import BlockCollisionShapes
from .types.block_loot import BlockLootEntry
from .types.blocks import Block
from .types.commands import Commands
from .types.effects import Effect
from .types.enchantments import Enchantment
from .types.entities import Entity
from .types.entity_loot import EntityLootEntry
from .types.features import FeatureEntry
from .types.foods import Food
from .types.instruments import Instrument
from .types.items import Item
from .types.language import EnUs
from .types.map_icons import MapIcon
from .types.materials import Materials
from .types.particles import Particle
from .types.protocol_versions import ProtocolVersion
from .types.sounds import Sound
from .types.version import Version
from .types.windows import Window

MINECRAFT_DATA_SUBMODULE = Path(__file__).parent / "minecraft-data"


class HasName(TypedDict):
    name: str


class HasIDName(TypedDict):
    id: int
    name: str


class HasStringIDName(TypedDict):
    id: str
    name: str


T = TypeVar("T")
HasNameT = TypeVar("HasNameT", bound=HasName)
HasIDNameT = TypeVar("HasIDNameT", bound=HasIDName | HasStringIDName)


@dataclass(frozen=True)
class Index(Generic[T]):
    items: list[T]


@dataclass(frozen=True)
class NameIndex(Index[HasNameT]):
    @cached_property
    def by_name(self):
        return {item["name"]: item for item in self.items}


@dataclass(frozen=True)
class IDNameIndex(NameIndex[HasIDNameT]):
    @cached_property
    def by_id(self):
        return {item["id"]: item for item in self.items}


@dataclass(frozen=True)
class BlockIndex(Index[Block]):
    @cached_property
    def by_state_id(self):
        result: dict[int, Block] = {}

        for item in self.items:
            if (min_state_id := item.get("minStateId")) is not None and (
                max_state_id := item.get("maxStateId")
            ) is not None:
                result.update(
                    dict.fromkeys(range(min_state_id, max_state_id + 1), item)
                )

        return result


@dataclass(frozen=True)
class BlockLootIndex(Index[BlockLootEntry]):
    @cached_property
    def by_block(self):
        result: dict[str, list[BlockLootEntry]] = {}

        for item in self.items:
            result.setdefault(item["block"], []).append(item)

        return result


class EntityLootIndex(Index[EntityLootEntry]):
    @cached_property
    def by_entity(self):
        result: dict[str, list[EntityLootEntry]] = {}

        for item in self.items:
            result.setdefault(item["entity"], []).append(item)

        return result


def underscore(word: str) -> str:
    # vendored from https://github.com/jpvanhal/inflection
    # SPDX-License-Identifier: MIT
    word = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", word)
    word = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", word)
    word = word.replace("-", "_")
    return word.lower()


class MinecraftDataMeta(type):
    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any]):  # pyright: ignore[reportExplicitAny]
        with (MINECRAFT_DATA_SUBMODULE / "data" / "dataPaths.json").open("rb") as f:
            attrs["data_paths"] = json.load(f)

        for edition in ("pc", "bedrock"):
            for path in (MINECRAFT_DATA_SUBMODULE / "data" / "pc" / "common").glob(
                "*.json"
            ):
                with path.open("rb") as f:
                    attrs[f"{edition}_" + underscore(path.stem)] = json.load(f)

            attrs[f"{edition}_versions_by_minecraft_version"] = {
                v["minecraftVersion"]: v for v in attrs[f"{edition}_protocol_versions"]
            }

            if edition == "pc":
                attrs["pre_netty_versions_by_protocol_version"] = {
                    v["version"]: v
                    for v in attrs[f"{edition}_protocol_versions"]
                    if not v["usesNetty"]
                }
                attrs["post_netty_versions_by_protocol_version"] = {
                    v["version"]: v
                    for v in attrs[f"{edition}_protocol_versions"]
                    if v["usesNetty"]
                }

        return super().__new__(cls, name, bases, attrs)


class MinecraftData(metaclass=MinecraftDataMeta):
    """
    Provides access to Minecraft data using the [minecraft-data](https://github.com/PrismarineJS/minecraft-data)
    repository. When this class is first created, a few common files will be read and parsed
    using blocking filesytem I/O, so you shouldn't import the class while running an async
    function.

    Version data is lazily loaded - nothing is parsed when constructing an instance of this
    class. To eagerly load everything, use the :meth:`load_collections` method.
    """

    if TYPE_CHECKING:
        # metaclass generated stuff
        bedrock_features: ClassVar[list[FeatureEntry]]
        bedrock_legacy: ClassVar[dict[Literal["blocks", "items"], dict[str, str]]]
        bedrock_protocol_versions: ClassVar[list[ProtocolVersion]]
        bedrock_versions_by_minecraft_version: ClassVar[dict[str, ProtocolVersion]]
        bedrock_versions: ClassVar[list[str]]

        pc_features: ClassVar[list[FeatureEntry]]
        pc_legacy: ClassVar[dict[Literal["blocks", "items"], dict[str, str]]]
        pc_protocol_versions: ClassVar[list[ProtocolVersion]]
        pc_versions_by_minecraft_version: ClassVar[dict[str, ProtocolVersion]]
        pc_versions: ClassVar[list[str]]

        pre_netty_versions_by_protocol_version: ClassVar[dict[int, ProtocolVersion]]
        post_netty_versions_by_protocol_version: ClassVar[dict[int, ProtocolVersion]]

        data_paths: ClassVar[dict[str, dict[str, dict[str, str]]]]

    def __init__(
        self,
        version: str,
        edition: Literal["pc", "bedrock"] = "pc",
    ):
        if version not in MinecraftData.data_paths[edition]:
            raise ValueError(f"unknown version {version} for edition {edition}")

        self._version_data_paths: dict[str, str] = MinecraftData.data_paths[edition][
            version
        ]
        self._data: dict[str, Any] = {}  # pyright: ignore[reportExplicitAny]

    @overload
    def _get_data(self, key: str) -> Any | None: ...  # pyright: ignore[reportExplicitAny]

    @overload
    def _get_data(self, key: str, default: T) -> Any | T: ...  # pyright: ignore[reportExplicitAny]

    def _get_data(self, key: str, default: T | None = None) -> Any | T | None:  # pyright: ignore[reportExplicitAny]
        if key in self._data:
            return self._data[key]

        data_path = (
            MINECRAFT_DATA_SUBMODULE / "data" / self._version_data_paths[key] / key
        ).with_suffix(".json")

        if not data_path.is_file():
            return default

        with data_path.open("rb") as f:
            self._data[key] = json.load(f)

        return self._data[key]

    @cached_property
    def available_data(self):
        return {underscore(k) for k in self._version_data_paths if k != "proto"}

    def load_collections(self, data_types: Sequence[str] | None = None):
        """
        Immediately load collections with names in `data_types`, or all collections
        if not specified.
        """

        for data_type, path in self._version_data_paths.items():
            if data_types is not None and data_type not in data_types:
                continue

            full_data_path = (
                MINECRAFT_DATA_SUBMODULE / "data" / path / data_type
            ).with_suffix(".json")

            if not full_data_path.is_file():
                continue

            with full_data_path.open("rb") as f:
                self._data[data_type] = json.load(f)

    @cached_property
    def attributes(self) -> NameIndex[Attribute]:
        return NameIndex(self._get_data("attributes", []))

    @cached_property
    def block_collision_shapes(self) -> BlockCollisionShapes | None:
        return self._get_data("blockCollisionShapes")

    @cached_property
    def blocks(self) -> BlockIndex:
        return BlockIndex(self._get_data("blocks", []))

    @cached_property
    def block_loot(self) -> BlockLootIndex:
        return BlockLootIndex(self._get_data("blockLoot", []))

    @cached_property
    def biomes(self) -> IDNameIndex[Biome]:
        return IDNameIndex(self._get_data("biomes", []))

    @cached_property
    def commands(self) -> Commands | None:
        return self._get_data("commands")

    @cached_property
    def effects(self) -> IDNameIndex[Effect]:
        return IDNameIndex(self._get_data("effects", []))

    @cached_property
    def enchantments(self) -> IDNameIndex[Enchantment]:
        return IDNameIndex(self._get_data("enchantments", []))

    @cached_property
    def entity_loot(self) -> EntityLootIndex:
        return EntityLootIndex(self._get_data("entityLoot", []))

    @cached_property
    def entities(self) -> IDNameIndex[Entity]:
        return IDNameIndex(self._get_data("entities", []))

    @cached_property
    def foods(self) -> IDNameIndex[Food]:
        return IDNameIndex(self._get_data("foods", []))

    @cached_property
    def instruments(self) -> IDNameIndex[Instrument]:
        return IDNameIndex(self._get_data("instruments", []))

    @cached_property
    def items(self) -> IDNameIndex[Item]:
        return IDNameIndex(self._get_data("items", []))

    @cached_property
    def language(self) -> EnUs | None:
        return self._get_data("language")

    @cached_property
    def login_packet(self) -> dict[str, Any] | None:  # pyright: ignore[reportExplicitAny]
        return self._get_data("loginPacket")

    @cached_property
    def map_icons(self) -> IDNameIndex[MapIcon]:
        return IDNameIndex(self._get_data("mapIcons", []))

    @cached_property
    def materials(self) -> Materials | None:
        return self._get_data("materials")

    @cached_property
    def particles(self) -> IDNameIndex[Particle]:
        return IDNameIndex(self._get_data("particles", []))

    @cached_property
    def protocol(self) -> dict[str, Any] | None:  # pyright: ignore[reportExplicitAny]
        return self._get_data("protocol")

    @cached_property
    def recipes(self) -> dict[str, Any] | None:  # pyright: ignore[reportExplicitAny]
        return self._get_data("recipes")

    @cached_property
    def sounds(self) -> IDNameIndex[Sound]:
        return IDNameIndex(self._get_data("sounds", []))

    @cached_property
    def tints(self) -> dict[str, Any] | None:  # pyright: ignore[reportExplicitAny]
        return self._get_data("tints")

    @cached_property
    def version(self) -> Version | None:
        return self._get_data("version")

    @cached_property
    def windows(self) -> IDNameIndex[Window]:
        return IDNameIndex(self._get_data("windows", []))
