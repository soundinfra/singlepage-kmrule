import unittest
from src import publish

class TestSiteDiff(unittest.TestCase):

    def test_blank_site(self):
        INDEX = "index.html"
        ERROR = "error.html"
        local = {INDEX: "1234", ERROR: "somehash"}
        self.assertEqual(publish.diff_files(local, {}), local)

    def test_update_site(self):
        local = {"index": "2"}
        remote = {"index": "1"}
        actual = publish.diff_files(local, remote)
        self.assertEqual(actual["index"], "2")

    def test_no_changes(self):
        local = {"index": "1234"}
        remote = {"index": "1234"}
        self.assertEqual(publish.diff_files(local, remote),{})

    def test_deleted_local_files(self):
        local = {"index.html": "1234"}
        remote = {"index.html": "1234", "error.html": "4554"}
        self.assertEqual(publish.diff_files(local, remote),{})


if __name__ == '__main__':
    unittest.main()