"""Tests for ``aurora.arb.hasher`` (stdlib unittest)."""

from __future__ import annotations

import hashlib
import unittest

from aurora.arb.hasher import compute_root_hash, sha256_hex


class TestHasher(unittest.TestCase):
    def test_sha256_hex_empty(self) -> None:
        expected = hashlib.sha256(b"").hexdigest()
        self.assertEqual(sha256_hex(b""), expected)

    def test_sha256_hex_known_vector(self) -> None:
        data = b"abc"
        self.assertEqual(
            sha256_hex(data),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )

    def test_compute_root_hash_matches_digest_of_manifest_bytes(self) -> None:
        manifest_bytes = b'{"a":1}'
        self.assertEqual(compute_root_hash(manifest_bytes), sha256_hex(manifest_bytes))


if __name__ == "__main__":
    unittest.main()
