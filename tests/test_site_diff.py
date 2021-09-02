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
        self.assertDictEqual(publish.diff_files(local, remote), local)

    def test_no_changes(self):
        local = {"index": "1234"}
        remote = {"index": "1234"}
        self.assertFalse(publish.diff_files(local, remote))

    def test_deleted_local_files(self):
        local = {"index.html": "1234"}
        remote = {"index.html": "1234", "error.html": "4554"}
        self.assertFalse(publish.diff_files(local, remote))


class TestSiteClean(unittest.TestCase):

    def test_blank_site(self):
        local = {"somefile": "somehash", "another": "hash"}
        self.assertFalse(publish.clean_files(local, {}))

    def test_update_site(self):
        local = {"index": "2"}
        remote = {"index": "1"}
        self.assertFalse(publish.clean_files(local, remote))

    def test_no_changes(self):
        local = {"index": "1234"}
        remote = {"index": "1234"}
        self.assertFalse(publish.clean_files(local, remote))

    def test_deleted_local_files(self):
        local = {"index.html": "1234"}
        remote = {"index.html": "1234", "error.html": "4554"}
        actual = publish.clean_files(local, remote)
        self.assertListEqual(actual, ["error.html"])


if __name__ == '__main__':
    unittest.main()
