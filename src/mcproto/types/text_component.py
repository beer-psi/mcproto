from typing import Literal, NotRequired, TypedDict


class PlainTextComponent(TypedDict):
    type: NotRequired[Literal["text"]]
    text: str


TranslatedTextComponent = TypedDict(
    "TranslatedTextComponent",
    {
        "type": NotRequired[Literal["translatable"]],
        "translate": str,
        "fallback": NotRequired[str],
        "with": NotRequired[list["TextComponent"]],
    },
)


class ScoreboardValue(TypedDict):
    name: str
    objective: str


class ScoreboardValueTextComponent(TypedDict):
    type: NotRequired[Literal["score"]]
    score: ScoreboardValue


class EntityNameTextComponent(TypedDict):
    type: NotRequired[Literal["selector"]]
    selector: str
    separator: NotRequired["TextComponent"]


class KeybindTextComponent(TypedDict):
    type: NotRequired[Literal["keybind"]]
    keybind: str


class NBTValuesTextComponent(TypedDict):
    type: NotRequired[Literal["nbt"]]
    source: NotRequired[Literal["block", "entity", "storage"]]
    nbt: str
    interpret: NotRequired[bool]
    separator: NotRequired["TextComponent"]
    block: NotRequired[str]
    entity: NotRequired[str]
    storage: NotRequired[str]


class ObjectTextComponent(TypedDict):
    type: NotRequired[Literal["object"]]
    atlas: NotRequired[str]
    sprite: str


TextComponent = (
    str
    | PlainTextComponent
    | TranslatedTextComponent
    | ScoreboardValueTextComponent
    | EntityNameTextComponent
    | KeybindTextComponent
    | NBTValuesTextComponent
    | ObjectTextComponent
)
