import logging
import unittest
from unittest.mock import patch

import src.soundinfra
from src import publish
from src.publish import PublishArgs


class TestPublish(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        logging.basicConfig(level=logging.ERROR)

    def test_no_args_exit_code_2(self):
        with self.assertRaises(SystemExit) as context:
            publish.setup([])
        self.assertEqual(2, context.exception.code)

    @patch.dict("os.environ", {src.publish.TOKEN_ENV_VAR: "token"},
                clear=True)
    def test_simple_happy_case(self):
        # Given
        domain = "example.com"

        # When
        args = publish.setup([domain])

        # Then
        self.assertEqual(args.domain, domain)
        self.assertEqual(args.directory, publish.PUBLISH_DIR)
        self.assertFalse(args.clean)

    @patch.dict("os.environ", {}, clear=True)
    def test_no_token_env_var(self):
        # Given
        domain = "example.com"
        # When
        with self.assertRaises(ValueError) as context:
            publish.setup([domain])
        # Then
        self.assertEqual("SoundInfra token SOUNDINFRA_TOKEN is not set.",
                         str(context.exception))

    @patch.dict("os.environ", {src.publish.TOKEN_ENV_VAR: ""}, clear=True)
    def test_blank_token_env_var(self):
        # Given
        domain = "example.com"
        # When
        with self.assertRaises(ValueError) as context:
            publish.setup([domain])
        # Then
        self.assertEqual("SoundInfra token SOUNDINFRA_TOKEN is not a valid "
                         "string.",
                         str(context.exception))

    def test_override_token(self):
        # Given
        domain = "example.com"
        token = "1234"

        # When
        args = publish.setup([domain, "--token", token])

        # Then
        self.assertEqual(args, PublishArgs(
            domain=domain, directory=publish.PUBLISH_DIR,
            dryrun=False, token=token, clean=False))

    @patch.dict("os.environ", {src.publish.TOKEN_ENV_VAR: "token"},
                clear=True)
    def test_override_directory(self):
        # Given
        domain = "example.com"
        directory = "somedir"

        # When
        args = publish.setup([domain, "--directory", directory])

        # Then
        self.assertEqual(args.directory, directory)

        # Also
        self.assertEqual(args.domain, domain)
        self.assertFalse(args.clean)

    @patch.dict("os.environ", {src.publish.TOKEN_ENV_VAR: "token"},
                clear=True)
    def test_set_clean(self):
        # Given
        domain = "example.com"

        # When
        args = publish.setup([domain, "--clean"])

        # Then
        self.assertTrue(args.clean)

        # Also
        self.assertEqual(args.domain, domain)
        self.assertEqual(args.directory, publish.PUBLISH_DIR)

    # Given
    @patch("builtins.input", return_value="foo")
    def test_verify_clean_no(self, mock_input):
        # When / Then
        self.assertFalse(publish.verify_clean(3, "foo"))

    # Given
    @patch("builtins.input", return_value="yes")
    def test_verify_clean_yes(self, mock_input):
        # When / Then
        self.assertTrue(publish.verify_clean(3, "foo"))

    @patch("src.soundinfra.SoundInfraClient")
    def test_publish_file_success(self, mock_client):
        # Given
        hash = "1234"
        mock_client.put.return_value = hash

        # When
        publish.publish_file(mock_client, "some.file", "somedir", hash)

    @patch("src.soundinfra.SoundInfraClient")
    def test_publish_file_failure(self, mock_client):
        # Given
        hash = "1234"
        mock_client.put.return_value = "1234 "

        # When
        with self.assertRaises(RuntimeError) as context:
            publish.publish_file(mock_client, "some.file", "somedir", hash)

        # Then
        self.assertEqual(
            str(context.exception),
            "Aborting due to failed hash mismatch for 'some.file'!!! "
            "(local '1234', returned: '1234 ').")
