import unittest
from unittest.mock import patch

from UI.Login.auth import register_reader


class RegisterReaderValidationTests(unittest.TestCase):
    @patch("UI.Login.auth.get_connection")
    def test_register_reader_rejects_non_gmail_email_before_database_write(self, mock_get_connection):
        success, message = register_reader("Test User", "test@yahoo.com", "Abc123$%")

        self.assertFalse(success)
        self.assertEqual(message, "Email must be a valid Gmail address.")
        mock_get_connection.assert_not_called()

    @patch("UI.Login.auth.get_connection")
    def test_register_reader_rejects_invalid_password_before_database_write(self, mock_get_connection):
        success, message = register_reader("Test User", "testuser@gmail.com", "abc12345")

        self.assertFalse(success)
        self.assertEqual(
            message,
            "Password must be 8-20 characters and include uppercase, lowercase, "
            "number, and special character.",
        )
        mock_get_connection.assert_not_called()


if __name__ == "__main__":
    unittest.main()
