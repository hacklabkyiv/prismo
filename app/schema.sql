CREATE TABLE IF NOT EXISTS admins
(
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users
(
    name     TEXT NOT NULL,
    key      TEXT NOT NULL,
    email    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS permissions
(
    device_id TEXT NOT NULL,
    user_key  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS event_logs
(
    device_id      TEXT      NOT NULL,
    user_key       TEXT,
    operation_type TEXT      NOT NULL,
    operation_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "devices"
(
    "id"               TEXT NOT NULL,
    "name"             TEXT NOT NULL,
    "type"             TEXT DEFAULT "tool",
    "slack_channel_id" TEXT DEFAULT NULL
);
