import unittest
from http import HTTPStatus

from src import SoundInfraClient

from unittest.mock import patch


class TestSoundInfraClient(unittest.TestCase):

    def test_blank_site_name(self):
        with self.assertRaises(ValueError) as context:
            SoundInfraClient("")
        self.assertEqual(
            "Domain name cannot be blank.", str(context.exception))

    def test_no_tld(self):
        with self.assertRaises(ValueError) as context:
            SoundInfraClient("notldhere")
        self.assertEqual("No Top-Level-Domain found in: \"notldhere\"",
                         str(context.exception))

    def test_invalid_chars(self):
        with self.assertRaises(ValueError) as context:
            SoundInfraClient("surprise!.com")
        self.assertEqual("Invalid character ! in domain name.",
                         str(context.exception))

    def test_too_long(self):
        long_domain_name = ".".join(8 * ("thiswillmakeareallylongdomainname",))
        with self.assertRaises(ValueError) as context:
            SoundInfraClient(long_domain_name)
        self.assertEqual("Domain name is too long (271 chars, max is 253)",
                         str(context.exception))

    @patch("http.client.HTTPSConnection")
    def test_get_conn(self, mock_conn):
        mysite = SoundInfraClient("my.site", conn=mock_conn)
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
        mysite = SoundInfraClient("my.site", conn=mock_conn)
        result = mysite._get_manifest_csv("token")

        # Then
        self.assertEqual(result, [b"one", b"two"])
        mock_conn.request.assert_called_with(
            "OPTIONS", "/", headers={"Authorization": "Bearer token"})
        mock_conn.getresponse.assert_called_once()
        mock_resp.readlines.assert_called_once()

    @patch("http.client.HTTPResponse")
    @patch("http.client.HTTPSConnection")
    def test_get_csv_unauthorized(self, mock_conn, mock_resp):
        # Given
        mock_resp.status = HTTPStatus.UNAUTHORIZED
        mock_conn.getresponse.return_value = mock_resp

        # When
        notasite = SoundInfraClient("not.a.site", conn=mock_conn)
        with self.assertRaises(RuntimeError) as context:
            notasite._get_manifest_csv("token")

        # Then
        mock_resp.readlines.assert_not_called()
        mock_conn.request.assert_called_with(
            "OPTIONS", "/", headers={"Authorization": "Bearer token"})
        self.assertEqual("Oops, got a 401", str(context.exception))