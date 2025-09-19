class MCProtoError(Exception):
    """
    The base class for all exceptions thrown by this library.
    """


class PacketParseError(MCProtoError):
    """
    Could not parse the received data for any reason. It is recommended
    that the connection be closed after getting this exception, since
    the protocol may be in an inconsistent state.
    """


class ProtocolError(MCProtoError):
    pass


class LocalProtocolError(ProtocolError):
    """
    Indicates an error due to local causes.

    This is raised when the connection is asked to do something that is
    incompatible with its state, for example, sending a packet after
    the connection has been closed.
    """


class RemoteProtocolError(ProtocolError):
    """
    Indicates an error due to the remote's actions.
    """
