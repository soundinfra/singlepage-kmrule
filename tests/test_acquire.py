import http.client
import unittest
from http import HTTPStatus

from src import Acquire

from unittest.mock import patch, MagicMock, Mock


class TestAcquire(unittest.TestCase):

    @patch("http.client.HTTPSConnection")
    def test_get_conn(self, mock_conn):
        mysite = Acquire(mock_conn)
        actual = mysite.conn
        self.assertEqual(mock_conn, actual)


    @patch("http.client.HTTPResponse")
    @patch("http.client.HTTPSConnection")
    def test_get_csv_success(self, mock_conn, mock_resp):
        mock_resp.status = HTTPStatus.OK
        csv_lines = ["one", "two"]
        mock_resp.readlines.return_value = csv_lines
        mock_conn.getresponse.return_value = mock_resp

        mysite = Acquire(mock_conn)
        result = mysite.read_remote_csv("token")
        self.assertEqual(result, csv_lines)
        mock_conn.getresponse.assert_called_once()
        mock_resp.readlines.assert_called_once()

    def get_csv_unauthorized(self):
        notasite = Acquire("notasite.com")
        notasite.read_remote_csv("token")
