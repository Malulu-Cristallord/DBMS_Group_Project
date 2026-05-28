import unittest
from unittest.mock import Mock, patch

from Backend.Functions.library_data import get_reader_by_id


class ReaderProfileLoadingTests(unittest.TestCase):
    @patch("Backend.Functions.library_data.get_connection")
    def test_get_reader_by_id_defaults_missing_daily_time_goal(self, mock_get_connection):
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {"column_name": "Reader_ID"},
            {"column_name": "Name"},
            {"column_name": "Email"},
            {"column_name": "Preferred_Category"},
            {"column_name": "Points"},
            {"column_name": "Receive_Recommendations"},
            {"column_name": "Show_Reading_History"},
            {"column_name": "Created_At"},
        ]
        mock_cursor.fetchone.return_value = {
            "Reader_ID": 4,
            "Name": "Reader Four",
            "Email": "reader4@gmail.com",
            "Preferred_Category": "Fiction",
            "Points": 10,
            "Receive_Recommendations": True,
            "Show_Reading_History": True,
            "Created_At": None,
            "Daily_Time_Goal": 60,
        }
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_connection

        reader = get_reader_by_id(4)

        self.assertEqual(reader["Reader_ID"], 4)
        self.assertEqual(reader["daily_time_goal"], 60)
        self.assertIn("60 AS `Daily_Time_Goal`", mock_cursor.execute.call_args_list[1].args[0])

    @patch("Backend.Functions.library_data.get_connection")
    def test_get_reader_by_id_accepts_point_alias(self, mock_get_connection):
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {"column_name": "Reader_ID"},
            {"column_name": "Name"},
            {"column_name": "Email"},
            {"column_name": "Point"},
        ]
        mock_cursor.fetchone.return_value = {
            "Reader_ID": 5,
            "Name": "Point Reader",
            "Email": "point.reader@gmail.com",
            "Preferred_Category": None,
            "Points": 7,
            "Receive_Recommendations": True,
            "Show_Reading_History": True,
            "Created_At": None,
            "Daily_Time_Goal": 60,
        }
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_connection

        reader = get_reader_by_id(5)

        self.assertEqual(reader["point"], 7)
        self.assertIn("`Point` AS `Points`", mock_cursor.execute.call_args_list[1].args[0])


if __name__ == "__main__":
    unittest.main()
