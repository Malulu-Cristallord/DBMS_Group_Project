import unittest
from unittest.mock import Mock, patch

from UI.Login.auth import login_reader, register_reader


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


class LoginReaderValidationTests(unittest.TestCase):
    @patch("UI.Login.auth.verify_password", return_value=True)
    @patch("UI.Login.auth.get_connection")
    def test_login_reader_normalizes_email_before_lookup(
        self,
        mock_get_connection,
        mock_verify_password,
    ):
        stored_reader = {
            "Reader_ID": 12,
            "Name": "Case Reader",
            "Email": "reader@gmail.com",
            "Password_Hash": "hashed-password",
            "Preferred_Category": "Fiction",
            "Points": 0,
            "Receive_Recommendations": True,
            "Show_Reading_History": True,
            "Created_At": None,
        }
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = stored_reader
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_connection

        success, message, reader = login_reader("  Reader@GMAIL.COM  ", "ReaderA1!")

        self.assertTrue(success)
        self.assertEqual(message, "Login successful.")
        self.assertEqual(reader["Reader_ID"], 12)
        mock_cursor.execute.assert_called_once()
        self.assertEqual(mock_cursor.execute.call_args.args[1], ("reader@gmail.com",))
        mock_verify_password.assert_called_once_with("ReaderA1!", "hashed-password")


if __name__ == "__main__":
    unittest.main()
