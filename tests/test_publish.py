import unittest
from unittest.mock import patch

import src.soundinfra
from src import publish
from src.publish import PublishArgs


class TestPublish(unittest.TestCase):

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

    @patch.dict("os.environ", {})
    def test_no_token_env_var(self):
        # Given
        domain = "example.com"
        # When
        with self.assertRaises(ValueError) as context:
            publish.setup([domain])
        # Then
        self.assertEqual("SoundInfra token SOUNDINFRA_TOKEN is not set.",
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
