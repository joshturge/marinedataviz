CREATE TABLE IF NOT EXISTS device (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    latitude REAL NOT NULL,
    longtitude REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS sensor (
    id INTEGER PRIMARY KEY,
    device_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    model TEXT NOT NULL,
    unit TEXT NOT NULL,
    unit_pretty TEXT NOT NULL,
    depth REAL,
    FOREIGN KEY (device_id)
        REFERENCES device(id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS observation (
    id INTEGER PRIMARY KEY,
    sensor_id INTEGER NOT NULL,
    time timestamp NOT NULL,
    value REAL NOT NULL,
    FOREIGN KEY (sensor_id)
        REFERENCES sensor(id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION
);
