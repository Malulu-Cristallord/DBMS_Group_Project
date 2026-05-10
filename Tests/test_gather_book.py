from Backend.Functions.library_data import *
from Backend.Functions.book_request import *

isbn = "9780439362139"
get_book_by_isbn(isbn)
cover_url = get_book_cover(isbn)
print(cover_url)