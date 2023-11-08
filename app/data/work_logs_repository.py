from app.data.device_dto import DeviceDto
from app.data.dtos import UserDto, OperationDto
from app.features.admin.init_app import get_db_connection

from sqlite3 import Row

def get_latest_key() -> str | None:
    """
    Get last triggered key, to add new users by clicking on any reader
    """
    connection = get_db_connection()
    rows = (
        connection.cursor()
        .execute(
            "SELECT user_key "
            "FROM event_logs "
            "WHERE user_key IS NOT NULL AND operation_type = 'deny_access' "
            "ORDER BY operation_time DESC LIMIT 1")
        .fetchone()
    )

    if rows is None:
        return None

    return rows[0]

def query_event_logs(start_time=None, end_time=None, limit=100):
    """
    Retrieve event logs from a SQLite database within a specified time range and limit the number of results.

    Args:
        start_time (str, optional): The start time of the time range to filter the logs. Should be in the format 'YYYY-MM-DD HH:MM:SS'.
        end_time (str, optional): The end time of the time range to filter the logs. Should be in the format 'YYYY-MM-DD HH:MM:SS'.
        limit (int, optional): The maximum number of log entries to retrieve. Default is 100.

    Returns:
        list of dict: A list of dictionaries representing the retrieved log entries. Each dictionary contains the following keys:
            - 'name' (str): User name.
            - 'key' (str): User key.
            - 'device_name' (str): Device(Reader) name.
            - 'device_id' (int): Device(Reader) ID.
            - 'operation_type' (str): Type of operation.
            - 'operation_time' (str): Time of the operation in 'YYYY-MM-DD HH:MM:SS' format.

    Example:
        # Retrieve logs for a specific time range and limit the results
        logs = query_event_logs(start_time='2023-01-01 00:00:00', end_time='2023-01-31 23:59:59', limit=50)
    """
    connection = get_db_connection()
    connection.row_factory = Row
    cursor = connection.cursor()

    query = """
        SELECT u.name, u.key, d.name, d.id, operation_type, operation_time
        FROM event_logs
        LEFT JOIN users u ON event_logs.user_key = u.key
        LEFT JOIN devices d ON d.id = event_logs.device_id
    """

    if start_time is not None and end_time is not None:
        query += "WHERE operation_time >= ? AND operation_time <= ?"
        cursor.execute(query + " ORDER BY operation_time DESC LIMIT ?", (start_time, end_time, limit))
    else:
        query += "ORDER BY operation_time DESC LIMIT ?"
        cursor.execute(query, (limit,))

    results = cursor.fetchall()

    # Convert the results to a list of dictionaries
    result_dicts = [dict(row) for row in results]

    # Don't forget to close the cursor and the connection when done
    cursor.close()
    #connection.close()

    return result_dicts

def get_full_logs():
    connection = get_db_connection()

    # Select all logins to devices, including of unregistered users.
    # These users marked as "Unknown".
    rows = (
        connection.cursor()
        .execute(
            "SELECT u.name, u.key, d.name, d.id, operation_type, operation_time FROM event_logs "
            "LEFT JOIN users u ON event_logs.user_key = u.key "
            "LEFT JOIN devices d ON d.id = event_logs.device_id "
            "ORDER BY operation_time DESC"
        )
        .fetchall()
    )

    work_log = []
    for user_name, user_key, device_name, device_id, operation_type, operation_time in rows:
        print(user_name, user_key, device_name, device_id, operation_type, operation_time)
        user = UserDto(user_key, user_name)
        device = DeviceDto(device_id, device_name)
        operation = OperationDto(operation_time, operation_type)

        log_entry = {
            "user": user,
            "device": device,
            "operation": operation,
        }
        work_log.append(log_entry)

    return work_log
