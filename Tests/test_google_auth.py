import unittest
from unittest.mock import Mock, patch

from UI.Login.auth import login_or_register_google_reader


class GoogleAuthTests(unittest.TestCase):
    @patch("UI.Login.auth.get_connection")
    def test_google_login_requires_verified_gmail_before_database_access(self, mock_get_connection):
        success, message, reader = login_or_register_google_reader(
            {
                "sub": "google-sub-1",
                "email": "reader@yahoo.com",
                "email_verified": True,
                "name": "Reader One",
            }
        )

        self.assertFalse(success)
        self.assertEqual(message, "Email must be a valid Gmail address.")
        self.assertIsNone(reader)
        mock_get_connection.assert_not_called()

    @patch("UI.Login.auth.get_connection")
    def test_google_login_links_existing_reader_by_verified_email(self, mock_get_connection):
        existing_reader = {
            "Reader_ID": 7,
            "Name": "Reader One",
            "Email": "reader@gmail.com",
            "Preferred_Category": "Fiction",
            "Points": 5,
            "Receive_Recommendations": True,
            "Show_Reading_History": True,
            "Created_At": None,
        }
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            {"total": 1},
            None,
            existing_reader,
        ]
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_connection

        success, message, reader = login_or_register_google_reader(
            {
                "sub": "google-sub-1",
                "email": "reader@gmail.com",
                "email_verified": True,
                "name": "Reader One",
            }
        )

        self.assertTrue(success)
        self.assertEqual(message, "Google login successful.")
        self.assertEqual(reader["Reader_ID"], 7)
        self.assertEqual(reader["Google_Sub"], "google-sub-1")
        mock_connection.commit.assert_called_once()

    @patch("UI.Login.auth.get_connection")
    def test_google_login_does_not_overwrite_existing_google_link(self, mock_get_connection):
        existing_reader = {
            "Reader_ID": 7,
            "Name": "Reader One",
            "Email": "reader@gmail.com",
            "Preferred_Category": "Fiction",
            "Points": 5,
            "Receive_Recommendations": True,
            "Show_Reading_History": True,
            "Created_At": None,
            "Google_Sub": "existing-google-sub",
        }
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            {"total": 1},
            None,
            existing_reader,
        ]
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_connection

        success, message, reader = login_or_register_google_reader(
            {
                "sub": "new-google-sub",
                "email": "reader@gmail.com",
                "email_verified": True,
                "name": "Reader One",
            }
        )

        self.assertFalse(success)
        self.assertEqual(message, "This email is already linked to another Google account.")
        self.assertIsNone(reader)
        mock_connection.commit.assert_not_called()

    @patch("UI.Login.auth.hash_password", return_value="hashed-google-placeholder")
    @patch("UI.Login.auth.get_connection")
    def test_google_login_creates_reader_when_email_is_new(
        self,
        mock_get_connection,
        mock_hash_password,
    ):
        created_reader = {
            "Reader_ID": 8,
            "Name": "New Reader",
            "Email": "newreader@gmail.com",
            "Preferred_Category": None,
            "Points": 0,
            "Receive_Recommendations": True,
            "Show_Reading_History": True,
            "Created_At": None,
            "Google_Sub": "google-sub-2",
        }
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            {"total": 1},
            None,
            None,
            created_reader,
        ]
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_connection

        success, message, reader = login_or_register_google_reader(
            {
                "sub": "google-sub-2",
                "email": "newreader@gmail.com",
                "email_verified": True,
                "name": "New Reader",
            }
        )

        self.assertTrue(success)
        self.assertEqual(message, "Google account created.")
        self.assertEqual(reader["Email"], "newreader@gmail.com")
        mock_hash_password.assert_called_once()
        mock_connection.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
