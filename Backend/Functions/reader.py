from Backend.DB_Stuff import db_connect


def save_reading_session_time(reader_ID, reading_session_time):
    print("Saving session time...")

    formatted_time = reading_session_time.strftime("%H:%M:%S")

    print("Formatted time = " , formatted_time)

    query = """
    UPDATE readers
    SET Time_Read = ADDTIME(Time_Read, %s)
    WHERE Reader_ID = %s
    """
    values = (formatted_time, reader_ID)

    db_connect.execute_query(query, values)

