from Backend.Functions import book_request


isbn = input("Insert ISBN: ").strip()
print(book_request.request_book_data(isbn))
