## cURL request for testing purposes

Emulate locking of RFID reader device:
```commandline
curl -X POST http://127.0.0.1:5000/devices/c8f3b540-7d3f-11ee-b962-0242ac120002/log_operation -H 'Content-Type: application/json' -d '{"operation": "lock", "key": "34"}'
```