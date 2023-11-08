## Api for readers

#### Get all keys with access to device

Method: GET
Path: `/reader/<device_id>/accesses/`
Response:

```json
{
  "keys": [
    "value_1",
    "value_2"
  ]
}
```

#### Log an operation

Method: POST
Path: `/reader/<device_id>/log_operation`
List of operations: `lock`, `unlock`, `deny_access`
Body for lock:

```json
{
  "operation": "lock"
}
```

Body for unlock:

```json
{
  "operation": "unlock",
  "data": {
    "key": "<user key>"
  }
}
```


Body for deny:

```json
{
  "operation": "deny_access",
  "data": {
    "key": "<user key>"
  }
}
```

#### Get event log data

Method: GET
Path: `/api/logs`
Query Parameters:

1. start_time (optional): The start time of the time range (format: 'YYYY-MM-DD HH:MM:SS').
2. end_time (optional): The end time of the time range (format: 'YYYY-MM-DD HH:MM:SS').
3. limit (optional): The maximum number of log entries to retrieve (default: 100).

Response:

```json
[
  {
    "id": "d2db5ec4-6e7a-11ee-b962-0242ac120002",
    "key": "2fc49ee397fc41a2c8721f86d7f87bb2c560c01d7b19bc1654fb5db9beaa19ad",
    "name": "MyTestCard",
    "operation_time": "2023-11-07 10:17:12",
    "operation_type": "lock"
  },
  // More log entries
}
```
Example usage

```
GET /api/log?start_time=2023-01-01%2012:00:00&end_time=2023-01-02%2012:00:00&limit=50
```
