## The database structure

The application creates the database by itself. The code for creating database is in `app/data/database.py` file.

### Project data structure

All data stored in postgres database. Currently, we have three tables:

- users - the table with users data
- devices - description of all RFID readers, registed in the system. Device has its name, unique id and type. Type can be
"tool"(when reader used for unlocking different tools and machines, e.g. lathe, mill etc) or
"door"(when reader used for opening doors).
- permissions - the table with permissions. It contains two columns: device_id and user_key. Device_id is unique id of
  device, user_key is key of user, who has access to this device.
- event_logs - the jornal of all events. It contains four columns: user_key, device_id, operation and time. Operation
  can be `lock`, `unlock`, ...
  
#### Database

We use the sqlite database, the file for database is stored in `database.db` file. The file is not created by default.
You need to create it manually. See section "Prepare database"

Schema of database:

```mermaid
classDiagram
    direction BT
    class devices {
        text id
        text name
        text type
    }
    class permissions {
        text device_id
        text user_key
    }

    class users {
        text name
        text key
    }

    class event_log {
        text user_key
        text device_id
        text operation
        text time
    }

    class admins {
        integer id
        text username
        text password
    }

    permissions --> devices
    work_logs --> devices
    work_logs --> users
    permissions --> users
```
