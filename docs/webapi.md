## API Documentation

This API provides endpoints for managing devices, users, and logs.

### Logs API

* **Get Logs:** `/api/logs`
    * Retrieve access logs for devices
    * **Parameters:**
        * `start_time`: Optional. Filter logs by start time (ISO 8601 format)
        * `end_time`: Optional. Filter logs by end time (ISO 8601 format)
        * `limit`: Optional. Limit the number of logs returned (default: 100)
        * `offset`: Optional. Specify the offset of the first log to return (default: 0)
    * **Response:**
        * `logs`: List of access log entries

### Devices API

* **Get Latest Key:** `/api/devices/latest_key`
    * Retrieve the latest generated device key

* **Get All Devices:** `/api/devices`
    * Retrieve all devices

* **Add Device:** `/api/devices`
    * Create a new device
    * **Request Body:**
        * `device_id`: Unique identifier for the device
        * `device_type`: Type of device (e.g., "tool", "sensor")
        * `name`: Optional. Name of the device

* **Update Device:** `/api/devices/<device_id>`
    * Update an existing device
    * **Request Body:**
        * `device_type`: Optional. New device type (e.g., "tool", "sensor")
        * `name`: Optional. New name for the device

* **Remove Device:** `/api/devices/<device_id>`
    * Delete an existing device

### Users API

* **Get User Permissions:** `/api/users`
    * Retrieve permissions for all users

* **Add User:** `/api/users`
    * Create a new user
    * **Request Body:**
        * `name`: Name of the user
        * `key`: Unique identifier for the user
        * `slack_id`: Optional. Slack ID of the user

* **Delete User:** `/api/users/<user_key>`
    * Delete an existing user

* **Add User Permission:** `/api/users/<user_key>/devices/<device_id>`
    * Grant a specific device permission to a user

* **Remove User Permission:** `/api/users/<user_key>/devices/<device_id>`
    * Revoke a specific device permission from a user