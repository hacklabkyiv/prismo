from app.data.database_driver import get_db_connection


def start_work(user_key, device_id):
    connection = get_db_connection()

    connection.cursor().execute(
        "INSERT INTO work_logs (user_key, device_id, start_time) values (?, ?, strftime('%s', 'now'))",
        (user_key, device_id),
    )

    connection.commit()
    connection.close()


def finish_work(user_key, device_id):
    connection = get_db_connection()

    connection.cursor().execute(
        "UPDATE work_logs SET end_time = strftime('%s', 'now') WHERE user_key = ? AND device_id = ?",
        (user_key, device_id),
    )

    connection.commit()
    connection.close()


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
