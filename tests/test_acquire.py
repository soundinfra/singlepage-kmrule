import unittest
from http import HTTPStatus

from src import Acquire

from unittest.mock import patch


class TestAcquire(unittest.TestCase):

    def test_blank_site_name(self):
        with self.assertRaises(ValueError) as context:
            Acquire("")
        self.assertEqual("Invalid site name: \"\".", str(context.exception))

    def test_no_tld(self):
        with self.assertRaises(ValueError) as context:
            Acquire("notldhere")
        self.assertEqual("No Top-Level-Domain for site: \"notldhere\"", str(context.exception))

    def test_invalid_chars(self):
        self.assertTrue(False)

    def test_too_long(self):
        self.assertTrue(False)

    @patch("http.client.HTTPSConnection")
    def test_get_conn(self, mock_conn):
        mysite = Acquire("my.site", conn=mock_conn)
        actual = mysite.conn
        self.assertEqual(mock_conn, actual)

    @patch("http.client.HTTPResponse")
    @patch("http.client.HTTPSConnection")
    def test_get_csv_success(self, mock_conn, mock_resp):
        # Given
        mock_resp.status = HTTPStatus.OK
        mock_resp.readlines.return_value = [b"one", b"two"]
        mock_conn.getresponse.return_value = mock_resp

        # When
        mysite = Acquire("my.site", conn=mock_conn)
        result = mysite.read_remote_csv("token")

        # Then
        self.assertEqual(result, ["one", "two"])
        mock_conn.getresponse.assert_called_once()
        mock_resp.readlines.assert_called_once()

    @patch("http.client.HTTPResponse")
    @patch("http.client.HTTPSConnection")
    def test_get_csv_unauthorized(self, mock_conn, mock_resp):
        # Given
        mock_resp.status = HTTPStatus.UNAUTHORIZED
        mock_conn.getresponse.return_value = mock_resp

        # When
        notasite = Acquire("not.a.site", conn=mock_conn)
        with self.assertRaises(RuntimeError) as context:
            notasite.read_remote_csv("token")

        # Then
        mock_resp.readlines.assert_not_called()
        self.assertEqual("Oops, got a 401", str(context.exception))
