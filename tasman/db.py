from flask import g
import sqlite3
from tasman.model import Device

DATABASE = "tasman.db"

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES |
                            sqlite3.PARSE_COLNAMES)
    db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_device(dbconn: sqlite3.Connection, device: Device):
    cur = dbconn.cursor()
    cur.execute("INSERT INTO device (id,name,description,latitude,longtitude) VALUES (?,?,?,?,?)",
                (device.id, device.name, device.description, device.latitude, device.longtitude))

    for sensor in device.sensors:
        cur.execute("INSERT INTO sensor (id,device_id,name,description,model,unit,unit_pretty,depth) VALUES (?,?,?,?,?,?,?,?)",
                    (sensor.id, device.id, sensor.name, sensor.description, sensor.model, sensor.unit, sensor.unit_pretty, sensor.depth))
        for obs in sensor.observations:
            cur.execute("INSERT INTO observation(id,sensor_id,time,value) VALUES (?,?,?,?)",
                    (obs.id, sensor.id, obs.time, obs.value))
    dbconn.commit()
