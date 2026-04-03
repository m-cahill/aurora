"""Tests for ``aurora.arb.canonical_json`` (stdlib unittest)."""

from __future__ import annotations

import unittest

from aurora.arb.canonical_json import canonicalize


class TestCanonicalJson(unittest.TestCase):
    def test_deterministic_bytes(self) -> None:
        obj = {"z": 1, "a": {"b": 2, "c": 3}}
        a = canonicalize(obj)
        b = canonicalize(obj)
        self.assertEqual(a, b)
        self.assertEqual(a.decode(), '{"a":{"b":2,"c":3},"z":1}')

    def test_rejects_float(self) -> None:
        with self.assertRaises(ValueError):
            canonicalize({"x": 1.0})

    def test_rejects_float_nested_dict(self) -> None:
        with self.assertRaises(ValueError):
            canonicalize({"a": {"b": 0.5}})

    def test_rejects_float_in_list(self) -> None:
        with self.assertRaises(ValueError):
            canonicalize({"a": [1, 2, 3.0]})

    def test_rejects_float_in_tuple(self) -> None:
        with self.assertRaises(ValueError):
            canonicalize({"a": (1.0,)})

    def test_accepts_int_bool_none(self) -> None:
        b = canonicalize({"a": True, "b": None, "c": 0})
        self.assertIn(b'"a":true', b)
        self.assertIn(b'"b":null', b)


if __name__ == "__main__":
    unittest.main()
