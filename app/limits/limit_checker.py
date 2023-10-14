import time
from dataclasses import dataclass

from app.data.database_driver import establish_connection


@dataclass
class Report:
    user_name: str
    device_name: str

    def __init__(self, user_name: str, device_name: str):
        self.user_name = user_name
        self.device_name = device_name


def check_devices_limits() -> list[Report]:
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            current_time = time.time()
            max_time = 100
            cursor.execute("""\
                SELECT sum(COALESCE(work_logs.end_time, %s) - work_logs.start_time) as total_use_time, 
                       user_key,
                       device_id,
                       d.name,
                       u.name
                FROM work_logs
                         join devices d on d.id = work_logs.device_id
                         join users u on u.key = work_logs.user_key
                GROUP BY user_key, device_id, d.name, u.name
                HAVING sum(COALESCE(work_logs.end_time, %s) - work_logs.start_time) > %s;""",
                           (current_time, current_time, max_time,))

            rows = cursor.fetchall()
            reports: list[Report] = []
            for row in rows:
                (sum_of_use, user_key, device_id, user_name, device_name) = row
                report = Report(user_name=user_name, device_name=device_name)
                reports.append(report)
        connection.commit()
    return reports
