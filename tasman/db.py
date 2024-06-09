from flask import g
import sqlite3
from tasman.model import Device, Sensor, Observation

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
    cur.execute("INSERT INTO device (name,description,latitude,longtitude) VALUES (?,?,?,?)",
                (device.name, device.description, device.latitude, device.longtitude))
    device_id = cur.lastrowid
    for sensor in device.sensors:
        cur.execute("INSERT INTO sensor (device_id,name,description,model,unit,unit_pretty,depth) VALUES (?,?,?,?,?,?,?)",
                    (device_id, sensor.name, sensor.description, sensor.model, sensor.unit, sensor.unit_pretty, sensor.depth))
        sensor_id = cur.lastrowid
        for obs in sensor.observations:
            cur.execute("INSERT INTO observation(sensor_id,time,value) VALUES (?,?,?)",
                    (sensor_id, obs.time, obs.value))
        
    dbconn.commit()

def get_device_by_id(dbconn: sqlite3.Connection, id: int) -> Device:
    ddata = query_db("SELECT id,name,description,latitude,longtitude FROM device WHERE id = ?", (id,), one=True)
    if ddata == None:
        raise Exception(f"{id}: device not found")

    name = ddata["name"]
    description = ddata["description"]
    latitude = ddata["latitude"]
    longtitude = ddata["longtitude"]
    device = Device(id, name, description, float(latitude), float(longtitude), [])

    sdata = query_db("SELECT id,name,description,model,unit,unit_pretty,depth FROM sensor WHERE device_id = ?", (int(id),))
    if sdata == None:
        raise Exception(f"{id}: sensors with device id not found")
    for sen in sdata:
        sensor = Sensor(int(sen["id"]), sen["name"], sen["description"], sen["model"], sen["unit"], sen["unit_pretty"], sen["depth"],  [])
        odata = query_db("SELECT id,time,value FROM observation WHERE sensor_id = ?", (int(sen["id"]),))
        if odata == None:
            raise Exception(f"{sen['id']}: observations with sensor id not found")
        for obs in odata:
            sensor.observations.append(Observation(int(obs["id"]), obs["time"], obs["value"]))
        device.sensors.append(sensor)
             
    return device
