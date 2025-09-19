`mcproto` is an implementation of the Minecraft multiplayer protocol. It is designed
to be embeddable in any program, async or sync. See the [Sans I/O specification] for
more information.

The library currently doesn't provide a concrete client/server implementation.

For parsing packets, the library uses PrismarineJS's [minecraft-data] repository,
ensuring that it can remain up-to-date with new Minecraft versions.

[Sans I/O specification]: https://sans-io.readthedocs.io/
[minecraft-data]: https://github.com/PrismarineJS/minecraft-data

## Usage

Let's assume you have some form of network socket available. The easiest way to
start is to create a connection for a specific version of Minecraft:

```python
from mcproto import ConnectionType, MinecraftConnection

connection = MinecraftConnection.for_version("1.21.8", ConnectionType.CLIENT)
```

Give the connection some data:

```python
connection.receive_data(socket.read())  # or any data buffer, really
```

and the connection will yield events as the data is parsed:

```python
for event in connection.events():
    # uh oh, the other side sent garbage, just give up and close
    if isinstance(event, CloseConnection):
        raise event.exc
    if isinstance(event, PacketReceived):
        packet = event.packet
        # handle the packets however you want
```

## NBT parser

The library contains a full fledged NBT parser at `mcproto.codecs.nbt`. It supports
all current NBT formats (big-endian, anonymous compounds, little-endian, network little-endian).
It provides a familiar API similar to `json` (`load`, `loads`, `dump`, `dumps`) and simplifies
the NBT into native Python objects:

```python
>>> import gzip
>>> from mcproto.codecs import nbt
>>> nbt.load(gzip.GzipFile("bigtest.nbt.gz"))
{
    'longTest': 9223372036854775807l,
    'shortTest': 32767s,
    'stringTest': 'HELLO WORLD THIS IS A TEST STRING ÅÄÖ!',
    'floatTest': 0.4982314705848694f,
    'intTest': 2147483647,
    'nested compound test': {
        'ham': {'name': 'Hampus', 'value': 0.75f},
        'egg': {'name': 'Eggbert', 'value': 0.5f}
    },
    'listTest (long)': [11l, 12l, 13l, 14l, 15l],
    'listTest (compound)': [
        {'name': 'Compound tag #0', 'created-on': 1264099775885l},
        {'name': 'Compound tag #1', 'created-on': 1264099775885l}
    ],
    'byteTest': 127b,
    'byteArrayTest (the first 1000 values of (n*n*255+n*7)%100, starting with n=0 (0, 62, 34, 16, 8, ...))': b'\x00>"\x10\x08\n\x1...',  # omitted
    'doubleTest': 0.4931287132182315
}
```

## License

Licensed under either of

- Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or https://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or https://opensource.org/licenses/MIT)

at your option.
