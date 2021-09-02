import unittest

from src import acquire


class TestAcquire(unittest.TestCase):

    def test_kmrule_com(self):
        acquire.get_csv("kmrule.com")