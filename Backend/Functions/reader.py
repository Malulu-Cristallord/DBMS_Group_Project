from Backend.DB_Stuff import db_connect


def save_reading_session_time(reader_ID, reading_session_time: int):
    print("Saving session time...")

    hours = reading_session_time // 3600
    minutes = (reading_session_time % 3600) // 60
    seconds = reading_session_time % 60

    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    print("Formatted time =", formatted_time)

    query = """
    UPDATE readers
    SET Time_Read = ADDTIME(Time_Read, %s)
    WHERE Reader_ID = %s
    """

    values = (formatted_time, reader_ID)

    db_connect.execute_query(query, values)