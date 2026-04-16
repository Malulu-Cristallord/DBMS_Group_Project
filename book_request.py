import requests
import sys

# Fetching data from Open Library API
user_input = input("Enter the ISBN number: ")

try:
    book_api = f"https://openlibrary.org/isbn/{user_input}.json"
    book_response = requests.get(book_api)
    book_data = book_response.json()

    author_id = book_data["authors"][0]["key"]
    author_api = f"https://openlibrary.org{author_id}.json"
    author_response = requests.get(author_api)
    author_data = author_response.json()

except KeyError:
    sys.exit("Unable to retrieve data. Check the ISBN number.")


# Formatting data
def format_subjects():
    try:
        subjects_list = book_data["subjects"]
        subjects_str = " / ".join(subjects_list)
        return subjects_str
    except KeyError:
        return "None"


def format_dewey():
    try:
        return book_data["dewey_decimal_class"][0]
    except KeyError:
        return "None"


author_name = author_data["name"]
subjects = format_subjects()
dewey = format_dewey()

row_data = {
    "myBook": {
        "copies": 1,
        "title": book_data["title"],
        "author": author_name.title(),
        "publication": book_data["publish_date"],
        "publisher": book_data["publishers"][0],
        "isbn": user_input,
        "subjects": subjects,
        "dewey": dewey
    }
}

print("Row added.", row_data["myBook"])