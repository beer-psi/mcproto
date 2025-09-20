import functools
import struct
from abc import ABC
from dataclasses import dataclass
from enum import IntEnum
from typing import ClassVar, Final, Generic, TypeVar, final, override

T = TypeVar("T")
NumericT = TypeVar("NumericT", int, float)

FLOAT_MAX: Final[float] = struct.unpack(">f", b"\x7f\x7f\xff\xff")[0]  # pyright: ignore[reportAny]
FLOAT_MIN: Final[float] = struct.unpack(">f", b"\xff\x7f\xff\xff")[0]  # pyright: ignore[reportAny]
DOUBLE_MAX: Final[float] = struct.unpack(">d", b"\x7f\xef\xff\xff\xff\xff\xff\xff")[0]  # pyright: ignore[reportAny]
DOUBLE_MIN: Final[float] = struct.unpack(">d", b"\xff\xef\xff\xff\xff\xff\xff\xff")[0]  # pyright: ignore[reportAny]


class TagID(IntEnum):
    END = 0x00
    BYTE = 0x01
    SHORT = 0x02
    INT = 0x03
    LONG = 0x04
    FLOAT = 0x05
    DOUBLE = 0x06
    BYTE_ARRAY = 0x07
    STRING = 0x08
    LIST = 0x09
    COMPOUND = 0x0A
    INT_ARRAY = 0x0B
    LONG_ARRAY = 0x0C


@dataclass(frozen=True)
class NBTValue(ABC, Generic[T]):
    """
    Base class for NBT values that cannot be represented using
    native Python types.
    """

    TAG: ClassVar[TagID]
    """The NBT tag representing this value."""

    value: T
    """The underlying Python value."""

    @override
    def __str__(self):
        return self.value.__str__()

    @override
    def __hash__(self):
        return self.value.__hash__()


@functools.total_ordering
@dataclass(frozen=True)
class NBTNumericValue(NBTValue[NumericT]):
    """
    Base class for numeric NBT types (byte, short, int, long, float, double).
    Implements rich comparison methods with other numeric values. Supports casting
    to :class:`int`, :class:`float` and :class:`complex`. For more advanced uses,
    access the underlying :attr:`value` directly.
    """

    MIN: ClassVar[int | float]
    """The smallest value that can be represented by this numeric type."""

    MAX: ClassVar[int | float]
    """The largest value that can be represented by this numeric type."""

    value: NumericT
    """The underlying Python numeric value."""

    def __post_init__(self):
        if self.value < self.MIN or self.value > self.MAX:
            raise ValueError(
                f"Value {self.value} is out of range for {self.__class__.__name__}"
            )

    def __int__(self):
        return self.value.__int__()

    def __float__(self):
        return self.value.__float__()

    def __complex__(self):
        return complex(self.value)

    @override
    def __eq__(self, other: object):
        if not isinstance(other, NBTValue):
            return self.value.__eq__(other)

        return self.value.__eq__(other.value)  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]

    def __lt__(self, other: object):
        if not isinstance(other, NBTValue):
            # This will return NotImplemented if float can't handle it, it's fine
            return self.value.__lt__(other)  # pyright: ignore[reportArgumentType]

        return self.value.__lt__(other.value)  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]


@final
@dataclass(frozen=True)
class NBTByte(NBTNumericValue[int]):
    TAG = TagID.BYTE
    MIN = -128
    MAX = 127

    @override
    def __repr__(self) -> str:
        return f"{self.value}b"


@final
@dataclass(frozen=True)
class NBTShort(NBTNumericValue[int]):
    TAG = TagID.SHORT
    MIN = -32768
    MAX = 32767

    @override
    def __repr__(self) -> str:
        return f"{self.value}s"


@final
@dataclass(frozen=True)
class NBTInt(NBTNumericValue[int]):
    TAG = TagID.INT
    MIN = -2147483648
    MAX = 2147483647

    @override
    def __repr__(self) -> str:
        return str(self.value)


@final
@dataclass(frozen=True)
class NBTLong(NBTNumericValue[int]):
    TAG = TagID.LONG
    MIN = -9223372036854775808
    MAX = 9223372036854775807

    @override
    def __repr__(self) -> str:
        return f"{self.value}l"


@final
@dataclass(frozen=True)
class NBTFloat(NBTNumericValue[float]):
    TAG = TagID.FLOAT
    MIN = FLOAT_MIN
    MAX = FLOAT_MAX

    @override
    def __repr__(self) -> str:
        return f"{self.value}f"


@final
@dataclass(frozen=True)
class NBTDouble(NBTNumericValue[float]):
    TAG = TagID.DOUBLE
    MIN = DOUBLE_MIN
    MAX = DOUBLE_MAX

    @override
    def __repr__(self) -> str:
        return str(self.value)
