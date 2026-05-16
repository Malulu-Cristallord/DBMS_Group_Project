from Backend.Functions.book_request import request_book_data

test_data = [9780141355429, 9780439362139, 9780007264179]
for data in test_data:
    request_book_data(data)