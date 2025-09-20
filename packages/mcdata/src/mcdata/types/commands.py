# pyright: reportDeprecated=false
from typing import Any, Literal, Required, TypedDict, Union


class _ArgumentNode(TypedDict, total=False):
    type: Required["_ArgumentNodeType"]
    """ Required property """

    name: Required[str]
    """ Required property """

    executable: Required[bool]
    """ Required property """

    redirects: Required[list[str]]
    """ Required property """

    children: Required[list["_ArgumentNodeChildrenItem"]]
    """ Required property """

    parser: "_ArgumentNodeParser"


_ArgumentNodeChildrenItem = Union["_LiteralNode", "_ArgumentNode"]
""" Aggregation type: oneOf """


class _ArgumentNodeParser(TypedDict, total=False):
    parser: str
    modifier: dict[str, Any] | None  # pyright: ignore[reportExplicitAny]


_ArgumentNodeType = Literal["argument"]
_ARGUMENTNODETYPE_ARGUMENT: Literal["argument"] = "argument"
"""The values for the '_ArgumentNodeType' enum"""


class _LiteralNode(TypedDict, total=False):
    type: Required["_LiteralNodeType"]
    """ Required property """

    name: Required[str]
    """ Required property """

    executable: Required[bool]
    """ Required property """

    redirects: Required[list[str]]
    """ Required property """

    children: Required[list["_LiteralNodeChildrenItem"]]
    """ Required property """


_LiteralNodeChildrenItem = Union["_LiteralNode", "_ArgumentNode"]
""" Aggregation type: oneOf """


_LiteralNodeType = Literal["literal"]
_LITERALNODETYPE_LITERAL: Literal["literal"] = "literal"
"""The values for the '_LiteralNodeType' enum"""


class _ParserInfo(TypedDict, total=False):
    parser: Required[str]
    """ Required property """

    modifier: Required[dict[str, Any] | None]  # pyright: ignore[reportExplicitAny]
    """ Required property """

    examples: Required[list[str]]
    """ Required property """


class Commands(TypedDict, total=False):
    root: Required["_RootNode"]
    """ Required property """

    parsers: Required[list["_ParserInfo"]]
    """ Required property """


class _RootNode(TypedDict, total=False):
    type: Required["_RootNodeType"]
    """ Required property """

    name: Required[str]
    """ Required property """

    executable: Required[bool]
    """ Required property """

    redirects: Required[list[str]]
    """ Required property """

    children: Required[list["_RootNodeChildrenItem"]]
    """ Required property """


_RootNodeChildrenItem = Union["_LiteralNode", "_ArgumentNode"]
""" Aggregation type: oneOf """


_RootNodeType = Literal["root"]
_ROOTNODETYPE_ROOT: Literal["root"] = "root"
"""The values for the '_RootNodeType' enum"""
