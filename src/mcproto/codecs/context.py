# pyright: reportMissingTypeArgument=false, reportAny=false, reportAttributeAccessIssue=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownVariableType=false
from typing import IO, TYPE_CHECKING, Any

from construct import Construct, Subconstruct

if TYPE_CHECKING:
    from construct import Context


class ContextParamsProvider(Subconstruct):
    def __init__(self, subcon: "Construct[Any, Any]", **contextkw: Any):
        super().__init__(subcon)
        self.contextkw: dict[str, Any] = contextkw

    def _parse(self, stream: IO[bytes], context: "Context", path: str):
        context._params.update(self.contextkw)
        return self.subcon._parse(stream, context, path)

    def _build(self, obj: object, stream: IO[bytes], context: "Context", path: str):
        context._params.update(self.contextkw)
        return self.subcon._build(obj, stream, context, path)
