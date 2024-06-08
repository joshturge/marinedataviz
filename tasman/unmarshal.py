import xml.etree.ElementTree as et
from tasman.model import Device, Sensor, Observation
from datetime import datetime

def unmarshal_device(data: bytes) -> Device:
    xmlroot = et.fromstring(data)
    feat = xmlroot.find(".//feature")
    if feat == None:
        raise Exception("feature not found")
    id = feat.get("id")
    if id == None:
        raise Exception("id not found")
    name = feat.get("name")
    if name == None:
        raise Exception("name not found")
    desc = feat.get("description")
    if desc == None:
        raise Exception("description not found")
    lat = feat.get("lat")
    if lat == None:
        raise Exception("lat not found")
    lng = feat.get("lng")
    if lng == None:
        raise Exception("lng not found")
    device = Device(int(id), name, desc, float(lat), float(lng), [])

    for sen in feat.findall("sensors/sensor"):
        id = sen.get("id")
        if id == None:
            raise Exception("sensor id not found")
        name = sen.get("name")
        if name == None:
            raise Exception("sensor name not found")
        desc = sen.get("description")
        if desc == None:
            raise Exception("sensor description not found")
        model = sen.get("model")
        if model == None:
            raise Exception("sensor model not found")
        unit = sen.get("phenomenon_uom")
        if unit == None:
            raise Exception("sensor phenomenon_uom not found")
        unit_pretty = sen.get("phenomenon_name")
        if unit_pretty == None:
            raise Exception("sensor phenomenon_name not found")
        depth = sen.get("depth")
        if depth == None:
            depth = "-1"

        sensor = Sensor(int(id), name, desc, model, unit, unit_pretty, float(depth), [])

        for obs in sen.findall("observations/observation"):
            id = obs.get("id")
            if id == None:
                raise Exception("observation id not found")
            time = obs.get("time")
            if time == None:
                raise Exception("observation time not found")
            value = obs.get("value")
            if value == None:
                raise Exception("observation value not found")

            sensor.observations.append(Observation(int(id), datetime.fromisoformat(time), float(value)))

        device.sensors.append(sensor)

    return device
