import sqlite3


class AccessLog:
    def __init__(self, device_id, user_key, operation_type, operation_time):
        self.device_id = device_id
        self.user_key = user_key
        self.operation_type = operation_type
        self.operation_time = operation_time

    @classmethod
    def get_full_log(cls, start_time=None, end_time=None, limit=100, offset=0):
        """
        Retrieve event logs from a SQLite database within a specified time range and limit the number
        of results.

        Args:
            start_time (str, optional): The start time of the time range to filter the logs. Should
        be in the format 'YYYY-MM-DD HH:MM:SS'.
            end_time (str, optional): The end time of the time range to filter the logs. Should be
        in the format 'YYYY-MM-DD HH:MM:SS'.
            limit (int, optional): The maximum number of log entries to retrieve. Default is 100.
            offset (int, optional): The offset from the beginning of the log entries to start
        retrieving results. Default is 0.

        Returns:
            list of dict: A list of dictionaries representing the retrieved log entries.
            Each dictionary contains the following keys:
                - 'name' (str): Username.
                - 'key' (str): User key.
                - 'device_name' (str): Device(Reader) name.
                - 'device_id' (int): Device(Reader) ID.
                - 'operation_type' (str): Type of operation.
                - 'operation_time' (str): Time of the operation in 'YYYY-MM-DD HH:MM:SS' format.

        Example:
            Retrieve logs for a specific time range and limit the results

            logs = query_event_logs(start_time='2023-01-01 00:00:00', end_time='2023-01-31 23:59:59',
            limit=50)
        """
        connection = sqlite3.connect('database.db')
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        query = """
            SELECT u.name, u.key, d.name, d.id, operation_type, operation_time
            FROM event_logs
            LEFT JOIN users u ON event_logs.user_key = u.key
            LEFT JOIN devices d ON d.id = event_logs.device_id
        """

        if start_time is not None and end_time is not None:
            query += "WHERE operation_time >= ? AND operation_time <= ?"
            cursor.execute(query + " ORDER BY operation_time DESC LIMIT ? OFFSET ?",
                           (start_time, end_time, limit, offset))
        else:
            query += "ORDER BY operation_time DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (limit, offset))

        results = cursor.fetchall()

        # Convert the results to a list of dictionaries
        result_dicts = [dict(row) for row in results]

        # Don't forget to close the cursor and the connection when done
        cursor.close()
        connection.close()
        return result_dicts
