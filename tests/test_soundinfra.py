import unittest
from pathlib import Path

from src import soundinfra as si


class TestSoundInfra(unittest.TestCase):

    def test_parse_svs_empty(self):
        self.assertDictEqual((si.parse_csv([])), {})

    def test_parse_csv_simple(self):
        self.assertDictEqual(si.parse_csv([b"hash,file.html"]),
                             {"file.html": "hash"})

    def test_parse_csv_strip_spaces(self):
        self.assertDictEqual(si.parse_csv([b"hash , file.html"]),
                             {"file.html": "hash"})

    def test_parse_csv_identical_hash(self):
        self.assertDictEqual(si.parse_csv(
            [b"hash , file.html", b"hash, file2.html"]),
            {"file.html": "hash", "file2.html": "hash"})

    def test_parse_csv_identical_filename(self):
        with self.assertRaises(ValueError) as context:
            si.parse_csv([b"hash , file.html", b"hash, file.html"])
        self.assertEqual("Error: Multiple entries for file: file.html.",
                         str(context.exception))

    # Extra columns are ignored
    def test_parse_csv_extra_columns(self):
        self.assertDictEqual(si.parse_csv([b"hash,file.html,hello"]),
                             {"file.html": "hash"})

    def test_parse_csv_missing_columns(self):
        with self.assertRaises(ValueError) as context:
            si.parse_csv([b"hash  file.html", b"hash, file.html"])
        self.assertEqual("Error: Expected two columns on line 1 of CSV.",
                         str(context.exception))

    def test_parse_csv_invalid_hash(self):
        with self.assertRaises(ValueError) as context:
            si.parse_csv([b"hash with spaces, file.html", b"hash, file.html"])
        self.assertEqual("Error: Hash on line 1 does not look valid.",
                         str(context.exception))

    def test_parse_invalid_utf8(self):
        with self.assertRaises(ValueError) as context:
            si.parse_csv([b"AB\xfc"])
        self.assertEqual("Error: Decode error on line 1 ('utf-8' codec " +
                         "can't decode byte 0xfc in position 2: invalid " +
                         "start byte).", str(context.exception))

    def test_build_manifest(self):
        # Given
        directory = "public"
        self.assertTrue(Path(directory).exists())

        # When
        manifest = si.build_manifest(directory)

        # Then
        self.assertGreater(len(manifest), 1)
        for name, hash in manifest.items():
            self.assertEqual(32, len(hash))

    def test_hash_file(self):
        # Given
        path = Path("public/index.html")

        # When
        hash, handle = si.hash_file(path)

        # Then
        self.assertTrue(handle.closed)
