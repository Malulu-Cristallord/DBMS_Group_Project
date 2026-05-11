from UI.Login.auth import login_or_register_google_reader


def _state_get(session_state, key, default=None):
    if hasattr(session_state, "get"):
        return session_state.get(key, default)
    return getattr(session_state, key, default)


def google_user_is_logged_in(user_info) -> bool:
    if hasattr(user_info, "get"):
        return bool(user_info.get("is_logged_in"))
    return bool(getattr(user_info, "is_logged_in", False))


def set_reader_session(session_state, reader: dict) -> None:
    session_state["logged_in"] = True
    session_state["reader_id"] = reader["Reader_ID"]
    session_state["reader_name"] = reader["Name"]
    session_state["reader_email"] = reader["Email"]
    session_state["preferred_category"] = reader.get("Preferred_Category")
    session_state["points"] = reader.get("Points", 0)


def sync_google_user_to_session(session_state, google_user) -> tuple[bool, str, dict | None]:
    if _state_get(session_state, "logged_in", False):
        return True, "Already signed in.", None

    if not google_user_is_logged_in(google_user):
        return False, "Google user is not signed in.", None

    success, message, reader = login_or_register_google_reader(google_user)

    if success and reader:
        set_reader_session(session_state, reader)

    return success, message, reader
