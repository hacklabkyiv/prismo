from app.data.database_driver import get_db_connection


def start_work(user_key, device_id) -> bool:
    connection = get_db_connection()

    is_device_in_use: bool = connection.cursor().execute(
        "SELECT count(*) FROM work_logs WHERE device_id = ? AND end_time IS NULL", (device_id,)
    ).fetchall()[0] == 0

    if not is_device_in_use:
        connection.cursor().execute(
            "INSERT INTO work_logs (user_key, device_id, start_time) "
            "VALUES (?, ?, strftime('%s', 'now'))",
            (user_key, device_id),
        )
        connection.commit()

    connection.close()
    return not is_device_in_use


def finish_work(device_id):
    connection = get_db_connection()

    connection.cursor().execute(
        "UPDATE work_logs "
        "SET end_time = strftime('%s', 'now')"
        "WHERE device_id = ? "
        "AND start_time = (SELECT MAX(start_time) "  # Update only latest one,
        "FROM work_logs "  # Based on start_time value
        "WHERE device_id = ?)",
        (device_id, device_id),
    )

    connection.commit()
    connection.close()


def get_latest_key():
    """
    Get last triggered key, to add new users by clicking on any reader
    """
    connection = get_db_connection()
    latest_key = (
        connection.cursor()
        .execute("SELECT user_key FROM work_logs ORDER BY start_time LIMIT 1")
        .fetchone()
    )[0]
    return latest_key


def get_full_logs():
    connection = get_db_connection()

    # Select all logins to devices, including of unregistered users.
    # These users marked as "Unknown".
    rows = (
        connection.cursor()
        .execute(
            "SELECT COALESCE(u.name, 'Unknown') AS user_name, "
            "w.user_key, w.device_id, datetime(w.start_time, 'unixepoch'), datetime(w.end_time, 'unixepoch') "
            "FROM work_logs AS w "
            "LEFT JOIN users AS u ON w.user_key = u.key;"
        )
        .fetchall()
    )
    work_log = []
    for user_name, user_key, device_name, start_time, end_time in rows:
        log_entry = {
            "user_name": user_name,
            "user_key": user_key,
            "device_name": device_name,
            "start_time": start_time,
            "end_time": end_time,
        }
        work_log.append(log_entry)

    connection.close()

    return work_log
