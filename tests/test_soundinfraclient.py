import unittest
from http import HTTPStatus

from src import SoundInfraClient

from unittest.mock import patch


class TestSoundInfraClient(unittest.TestCase):

    def test_blank_site_name(self):
        with self.assertRaises(ValueError) as context:
            SoundInfraClient("", "token")
        self.assertEqual(
            "Domain name cannot be blank.", str(context.exception))

    def test_no_tld(self):
        with self.assertRaises(ValueError) as context:
            SoundInfraClient("notldhere", "token")
        self.assertEqual("No Top-Level-Domain found in: \"notldhere\".",
                         str(context.exception))

    def test_invalid_chars(self):
        with self.assertRaises(ValueError) as context:
            SoundInfraClient("surprise!.com", "token")
        self.assertEqual("Invalid character ! in domain name.",
                         str(context.exception))

    def test_too_long(self):
        long_domain_name = ".".join(8 * ("thiswillmakeareallylongdomainname",))
        with self.assertRaises(ValueError) as context:
            SoundInfraClient(long_domain_name, "token")
        self.assertEqual("Domain name is too long (271 chars, max is 253).",
                         str(context.exception))

    @patch("http.client.HTTPSConnection")
    def test_get_conn(self, mock_conn):
        mysite = SoundInfraClient("my.site", "token", conn=mock_conn)
        actual = mysite.conn
        self.assertEqual(mock_conn, actual)

    @patch("http.client.HTTPResponse")
    @patch("http.client.HTTPSConnection")
    def test_get_manifest_success(self, mock_conn, mock_resp):
        # Given
        mock_resp.status = HTTPStatus.OK
        mock_resp.readlines.return_value = [b"hash1,index.html"]
        mock_conn.getresponse.return_value = mock_resp

        # When
        mysite = SoundInfraClient("my.site", "token", conn=mock_conn)
        result = mysite.get_manifest()

        # Then
        self.assertDictEqual(result, {"index.html": "hash1"})
        mock_conn.request.assert_called_with(
            "OPTIONS", "/",
            headers={"Authorization": "Bearer token"},
            body=None)
        mock_conn.getresponse.assert_called_once()
        mock_resp.readlines.assert_called_once()

    @patch("http.client.HTTPResponse")
    @patch("http.client.HTTPSConnection")
    def test_get_csv_unauthorized(self, mock_conn, mock_resp):
        # Given
        mock_resp.status = HTTPStatus.UNAUTHORIZED
        mock_conn.getresponse.return_value = mock_resp

        # When
        notasite = SoundInfraClient("not.a.site", "token", conn=mock_conn)
        with self.assertRaises(RuntimeError) as context:
            notasite.get_manifest()

        # Then
        mock_resp.readlines.assert_not_called()
        mock_conn.request.assert_called_with(
            "OPTIONS", "/", headers={"Authorization": "Bearer token"},
            body=None)
        self.assertEqual("Oops, got a 401.", str(context.exception))

    @patch("http.client.HTTPResponse")
    @patch("http.client.HTTPSConnection")
    def test_put_success(self, mock_conn, mock_resp):
        # Given
        mock_resp.status = HTTPStatus.OK
        mock_resp.readlines.return_value = [b"hash1/blank.html"]
        mock_conn.getresponse.return_value = mock_resp

        # When
        mysite = SoundInfraClient("my.site", "token", conn=mock_conn)
        result = mysite.put("tests/data", "blank.html")

        # Then
        mock_conn.request.assert_called_with(
            "PUT",
            "/blank.html",
            headers={"Authorization": "Bearer token"},
            body=b'')
        mock_conn.getresponse.assert_called_once()
        mock_resp.readlines.assert_called_once()
        self.assertEqual('hash1', result)

    @patch("http.client.HTTPResponse")
    @patch("http.client.HTTPSConnection")
    def test_delete_success(self, mock_conn, mock_resp):
        # Given
        mock_resp.status = HTTPStatus.OK
        mock_resp.readlines.return_value = [b"hash1/blank.html"]
        mock_conn.getresponse.return_value = mock_resp

        # When
        mysite = SoundInfraClient("my.site", "token", conn=mock_conn)
        result = mysite.put("tests/data", "blank.html")

        # Then
        mock_conn.request.assert_called_with(
            "PUT",
            "/blank.html",
            headers={"Authorization": "Bearer token"},
            body=b'')
        mock_conn.getresponse.assert_called_once()
        mock_resp.readlines.assert_called_once()
        self.assertEqual('hash1', result)
