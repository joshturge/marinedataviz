from dataclasses import dataclass
import xml.etree.ElementTree as et 
from flask import Flask, render_template, request

@dataclass
class Observation:
    id: int
    time: int
    value: float

@dataclass
class Sensor:
    id: int
    name: str
    description: str
    model: str
    unit: str
    unit_pretty: str
    meta: dict[str, str]
    observations: list[Observation]

@dataclass
class Device:
    id: int
    name: str
    description: str
    active: bool
    latitude: float
    longtitude: float
    sensors: list[Sensor]

def unmarshal_device(xmlroot: et.Element) -> Device:
    observations = [Observation(1, 1, 1)]
    sensors = [Sensor(1, "sensor", "description", "model", "unit", "Unit", {}, observations)]
    dev = Device(1, "device", "description", True, 0, 0, sensors)
    return dev

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

    return render_template("device_stats.html", device=device), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
