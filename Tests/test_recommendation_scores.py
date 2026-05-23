import unittest

from Backend.Functions.library_data import calculate_personalized_score, calculate_popular_score


class RecommendationScoreTests(unittest.TestCase):
    def test_personalized_score_uses_rating_click_saved_and_category_match(self):
        book = {
            "avg_rating": 4.0,
            "clicked": 5,
            "saved": 2,
            "_max_clicked": 10,
            "_max_saved": 4,
            "genre": "Fiction",
        }
        reader = {"Preferred_Category": "Fiction, Mystery"}

        score = calculate_personalized_score(book, reader)

        self.assertEqual(score, 0.72)

    def test_popular_score_omits_category_match(self):
        book = {
            "avg_rating": 4.0,
            "clicked": 5,
            "saved": 2,
            "_max_clicked": 10,
            "_max_saved": 4,
            "genre": "Fiction",
        }

        score = calculate_popular_score(book)

        self.assertEqual(score, 0.62)

    def test_scores_avoid_division_by_zero(self):
        book = {
            "avg_rating": 5.0,
            "clicked": 5,
            "saved": 2,
            "_max_clicked": 0,
            "_max_saved": 0,
            "genre": "History",
        }
        reader = {"Preferred_Category": "Fiction"}

        self.assertEqual(calculate_personalized_score(book, reader), 0.4)
        self.assertEqual(calculate_popular_score(book), 0.4)


if __name__ == "__main__":
    unittest.main()
