def decode_modified_utf8(s: bytes) -> str:
    """
    Decodes a bytestring containing MUTF-8 as defined in section
        4.4.7 of the JVM specification.

        :param s: A byte/buffer-like to be converted.
        :returns: A unicode representation of the original string.
    """

def encode_modified_utf8(u: str) -> bytes:
    """
    Encodes a unicode string as MUTF-8 as defined in section
        4.4.7 of the JVM specification.

        :param u: Unicode string to be converted.
        :returns: The encoded string as a `bytes` object.
    """
