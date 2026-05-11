import unittest

from UI.Login.validators import validate_google_email, validate_password


class ValidatorTests(unittest.TestCase):
    def test_validate_google_email_accepts_valid_gmail_addresses(self):
        valid_emails = [
            "testuser@gmail.com",
            "reader2026@gmail.com",
            "student123@gmail.com",
        ]

        for email in valid_emails:
            with self.subTest(email=email):
                self.assertEqual(validate_google_email(email), (True, ""))

    def test_validate_google_email_rejects_invalid_or_non_gmail_addresses(self):
        invalid_emails = [
            "test@yahoo.com",
            "test@icloud.com",
            "test@gmail",
            "test",
            "test@google.com",
        ]

        for email in invalid_emails:
            with self.subTest(email=email):
                is_valid, message = validate_google_email(email)
                self.assertFalse(is_valid)
                self.assertEqual(message, "Email must be a valid Gmail address.")

    def test_validate_password_accepts_required_password_format(self):
        valid_passwords = [
            "Abc123$%",
            "Student01$",
            "Reader2026!",
        ]

        for password in valid_passwords:
            with self.subTest(password=password):
                self.assertEqual(validate_password(password), (True, ""))

    def test_validate_password_rejects_missing_required_character_classes(self):
        invalid_passwords = [
            "abc12345",
            "ABC12345",
            "Abcdefgh",
            "Abc12345",
        ]

        for password in invalid_passwords:
            with self.subTest(password=password):
                is_valid, message = validate_password(password)
                self.assertFalse(is_valid)
                self.assertEqual(
                    message,
                    "Password must be 8-20 characters and include uppercase, "
                    "lowercase, number, and special character.",
                )

    def test_validate_password_rejects_spaces_and_non_ascii_characters(self):
        invalid_passwords = [
            "Abc 123$",
            "測試Abc123$",
        ]

        for password in invalid_passwords:
            with self.subTest(password=password):
                is_valid, message = validate_password(password)
                self.assertFalse(is_valid)
                self.assertEqual(
                    message,
                    "Password may only contain English letters, numbers, and "
                    "these special characters: ! @ # $ % ^ & * _ -.",
                )

    def test_validate_password_rejects_length_outside_allowed_range(self):
        invalid_passwords = [
            "Ab1$",
            "Abc1234567890123456$%",
        ]

        for password in invalid_passwords:
            with self.subTest(password=password):
                is_valid, message = validate_password(password)
                self.assertFalse(is_valid)
                self.assertEqual(
                    message,
                    "Password must be 8-20 characters and include uppercase, "
                    "lowercase, number, and special character.",
                )


if __name__ == "__main__":
    unittest.main()
