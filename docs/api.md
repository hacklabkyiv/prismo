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
Path: `/reader/<device_id>/operation`
List of operations: `lock`, `unlock`
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