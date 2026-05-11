import unittest
from unittest.mock import patch

from UI.Login.session import google_user_is_logged_in, set_reader_session, sync_google_user_to_session


class StreamlitUserWithoutLoginAttribute(dict):
    def __getattr__(self, key):
        raise AttributeError(f'st.user has no attribute "{key}".')


class LoginSessionTests(unittest.TestCase):
    def test_set_reader_session_preserves_existing_reader_session_keys(self):
        session_state = {}
        reader = {
            "Reader_ID": 3,
            "Name": "Reader Three",
            "Email": "reader3@gmail.com",
            "Preferred_Category": "Fiction",
            "Points": 10,
        }

        set_reader_session(session_state, reader)

        self.assertTrue(session_state["logged_in"])
        self.assertEqual(session_state["reader_id"], 3)
        self.assertEqual(session_state["reader_name"], "Reader Three")
        self.assertEqual(session_state["reader_email"], "reader3@gmail.com")
        self.assertEqual(session_state["preferred_category"], "Fiction")
        self.assertEqual(session_state["points"], 10)

    def test_google_user_is_logged_in_handles_missing_attribute(self):
        user_info = StreamlitUserWithoutLoginAttribute()

        self.assertFalse(google_user_is_logged_in(user_info))

    @patch("UI.Login.session.login_or_register_google_reader")
    def test_sync_google_user_to_session_uses_google_reader(self, mock_google_login):
        session_state = {"logged_in": False}
        google_user = {"is_logged_in": True}
        mock_google_login.return_value = (
            True,
            "Google login successful.",
            {
                "Reader_ID": 4,
                "Name": "Reader Four",
                "Email": "reader4@gmail.com",
                "Preferred_Category": None,
                "Points": 0,
            },
        )

        success, message, reader = sync_google_user_to_session(session_state, google_user)

        self.assertTrue(success)
        self.assertEqual(message, "Google login successful.")
        self.assertEqual(reader["Reader_ID"], 4)
        self.assertTrue(session_state["logged_in"])
        self.assertEqual(session_state["reader_id"], 4)


if __name__ == "__main__":
    unittest.main()
