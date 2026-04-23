from db_connect_Webb import get_connection

connection = get_connection()

if connection is not None and connection.is_connected():
    print("成功連線到 MySQL database")
    print("目前資料庫：", connection.database)

    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    print("目前 tables：")
    for table in tables:
        print(table[0])

    cursor.close()
    connection.close()
else:
    print("資料庫連線失敗")