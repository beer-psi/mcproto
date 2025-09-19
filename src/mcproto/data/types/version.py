from typing import TypedDict


class Version(TypedDict, total=False):
    """
    version.

    uniqueItems: True
    """

    version: int
    """ The protocol version """

    minecraftVersion: str
    """ pattern: ([0-9]+\\.[0-9]+(\\.[0-9]+)?[a-z]?(-pre[0-9]+)?)|([0-9]{2}w[0-9]{2}[a-z]) """

    majorVersion: str
    """ pattern: [0-9]+\\.[0-9]+[a-z]? """

    releaseType: str
    """ pattern: [a-z]+ """
