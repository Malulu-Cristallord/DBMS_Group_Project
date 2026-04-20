import requests
import sys
import json

# Notes: The current db source, Open Library, is still our best choice when it comes to fetching books.
# However, the db seems to have a major lack of books in Asian language.
# I will try to use more APIs if possible, and keep them free cause even the biggest dbs I can find still have big holes in them.
# -Malu

def request_book_data(user_input):
    try:
        book_api = f"https://openlibrary.org/isbn/{user_input}.json"
        book_response = requests.get(book_api)
        book_data = book_response.json()

        author_id = book_data["authors"][0]["key"]
        author_api = f"https://openlibrary.org{author_id}.json"
        author_response = requests.get(author_api)
        author_data = author_response.json()

        # Print the whole JSON for testing
        print(json.dumps(book_data, indent=4))
        # Test stat = 9780439362139 (Harry Potter 1)

    except KeyError:
        sys.exit("Unable to retrieve data. Check the ISBN number.")

def request_book_data_with_returning_value(user_input):
    try:
        book_api = f"https://openlibrary.org/isbn/{user_input}.json"
        book_response = requests.get(book_api)
        book_data = book_response.json()

        author_id = book_data["authors"][0]["key"]
        author_api = f"https://openlibrary.org{author_id}.json"
        author_response = requests.get(author_api)
        author_data = author_response.json()

        return json.dumps(book_data, indent=4)
        # Test stat = 9780439362139 (Harry Potter 1)

    except KeyError:
        sys.exit("Unable to retrieve data. Check the ISBN number.")






# Formatting data
def format_subjects(book_data):
    try:
        subjects_list = book_data["subjects"]
        subjects_str = " / ".join(subjects_list)
        return subjects_str
    except KeyError:
        return "None"


def format_dewey(book_data):
    try:
        return book_data["dewey_decimal_class"][0]
    except KeyError:
        return "None"





