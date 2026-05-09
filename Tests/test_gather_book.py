from Backend.Functions.library_data import get_book_by_isbn

books = get_book_by_isbn("9780439362139")
for book in books:
    print(book["Title"])
    print(book["ISBN"])
    print(book["Description"])
    print(book["Author"])