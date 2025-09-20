from enum import Enum


class MultiplayerState(Enum):
    HANDSHAKING = "handshaking"
    STATUS = "status"
    LOGIN = "login"
    CONFIGURATION = "configuration"
    PLAY = "play"
