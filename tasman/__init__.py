from dataclasses import dataclass
import xml.etree.ElementTree as et 
from datetime import datetime
import pandas as pd
from matplotlib.figure import Figure
from io import BytesIO
import base64
from flask import Flask, render_template, request

@dataclass
class Observation:
    id: int
    time: datetime 
    value: float

@dataclass
class Sensor:
    id: int
    name: str
    description: str
    model: str
    unit: str
    unit_pretty: str
    depth: float 
    observations: list[Observation]

@dataclass
class Device:
    id: int
    name: str
    description: str
    latitude: float
    longtitude: float
    sensors: list[Sensor]

def unmarshal_device(xmlroot: et.Element) -> Device:
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

def get_dataframe(observs: list[Observation]):
    time = []
    values = []
    for obs in observs:
        time.append(obs.time)
        values.append(obs.value)
    dataframe = pd.DataFrame({'time': time, 'values': values})
    dataframe.set_index('time', inplace=True)
    return dataframe

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("upload_form.html") 

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return "file not found", 400 
    file = request.files['file']
    xmlroot = et.fromstring(file.stream.read())
    device = unmarshal_device(xmlroot)

    plots = [] 
    for sensor in device.sensors:
        df = get_dataframe(sensor.observations)
        fig = Figure()
        ax = fig.subplots()
        ax.plot(df.index, df.values)
        if sensor.depth != 0:
            ax.set_title(f"{sensor.name} at depth of {sensor.depth:.2f} metres")
        else:
            ax.set_title(f"{sensor.name}")
        ax.tick_params(axis='x', labelrotation=30)
        # Save it to a temporary buffer.
        buf = BytesIO()
        fig.savefig(buf, format="png")
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        plots.append(data)


    return render_template("device_stats.html", device=device, plots=plots), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
