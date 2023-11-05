from app.data.device_dto import DeviceDto
from app.data.dtos import UserDto, OperationDto
from app.features.admin.init_app import get_db_connection


def get_latest_key() -> str | None:
    """
    Get last triggered key, to add new users by clicking on any reader
    """
    connection = get_db_connection()
    rows = (
        connection.cursor()
        .execute("""
        SELECT user_key 
        FROM event_logs 
        WHERE user_key IS NOT NULL 
        ORDER BY operation_time LIMIT 1""")
        .fetchone()
    )

    if rows is None:
        return None
    else:
        return rows[0]


def get_full_logs():
    connection = get_db_connection()

    # Select all logins to devices, including of unregistered users.
    # These users marked as "Unknown".
    rows = (
        connection.cursor()
        .execute(
            "SELECT u.name, u.key, d.name, d.id, operation_type, operation_time FROM event_logs "
            "LEFT JOIN users u ON event_logs.user_key = u.key "
            "JOIN devices d ON d.id = event_logs.device_id "
            "ORDER BY operation_time DESC"
        )
        .fetchall()
    )

    work_log = []
    for user_name, user_key, device_name, device_id, operation_type, operation_time in rows:
        print(user_name, user_key, device_name, device_id, operation_type, operation_time)
        user = UserDto(user_name, user_key)
        device = DeviceDto(device_name, device_id)
        operation = OperationDto(operation_time, operation_type)

        log_entry = {
            "user": user,
            "device": device,
            "operation": operation,
        }
        work_log.append(log_entry)

    return work_log
