import pytest

from services import crypto


def _channel_pair():
    client_private, client_public = crypto.generate_keypair()
    server_private, server_public = crypto.generate_keypair()
    server_root = crypto.derive_root(server_private, client_public)
    client_root = crypto.derive_root(client_private, server_public)
    assert server_root == client_root
    return crypto.SecureChannel(server_root), crypto.SecureChannel(client_root)


def test_roundtrip():
    server, client = _channel_pair()
    envelope = client.encrypt(b"hello lucid", "c2s")
    assert server.decrypt(envelope, "c2s") == b"hello lucid"


def test_padding_hides_length():
    server, client = _channel_pair()
    short = client.encrypt(b"a", "c2s")
    longer = client.encrypt(b"a" * 50, "c2s")
    assert len(short["ct"]) == len(longer["ct"])


def test_replay_rejected():
    server, client = _channel_pair()
    envelope = client.encrypt(b"once", "c2s")
    assert server.decrypt(envelope, "c2s") == b"once"
    with pytest.raises(ValueError):
        server.decrypt(envelope, "c2s")


def test_tampered_ciphertext_rejected():
    server, client = _channel_pair()
    envelope = client.encrypt(b"data", "c2s")
    envelope["ct"] = envelope["ct"][:-4] + "AAAA"
    with pytest.raises(Exception):
        server.decrypt(envelope, "c2s")
