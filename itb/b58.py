"""Base58 (Bitcoin alphabet) as Solana uses it for keys, hashes and signatures."""

ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_INDEX = {c: i for i, c in enumerate(ALPHABET)}


def encode(data):
    data = bytes(data)
    n = int.from_bytes(data, "big")
    out = []
    while n:
        n, r = divmod(n, 58)
        out.append(ALPHABET[r])
    pad = len(data) - len(data.lstrip(b"\0"))
    return "1" * pad + "".join(reversed(out))


def decode(text):
    n = 0
    for c in text:
        if c not in _INDEX:
            raise ValueError("not base58: %r" % c)
        n = n * 58 + _INDEX[c]
    body = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    pad = len(text) - len(text.lstrip("1"))
    return b"\0" * pad + body
