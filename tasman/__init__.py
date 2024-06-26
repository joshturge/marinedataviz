import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from tasman.unmarshal import unmarshal_device
from tasman.model import Device, Observation
from tasman.db import get_db, insert_device, query_db, get_device_by_id
from io import BytesIO
import base64
from flask import Flask, render_template, request, g

def get_dataframe(observs: list[Observation]):
    time = []
    values = []
    for obs in observs:
        time.append(obs.time)
        values.append(obs.value)
    dataframe = pd.DataFrame({"time": time, "values": values})
    dataframe.set_index('time', inplace=True)
    return dataframe

def get_plots(device: Device) -> list[str]:
    """get_plots generates plots in png format encoded as ascii, which can then be embedded into the html img element"""
    plots = [] 
    for sensor in device.sensors:
        df = get_dataframe(sensor.observations)
        # remove anomalies from dataset
        df = df.resample('D').mean().fillna(-1)
        df = df[np.abs(df.values-df.values.mean()) <= (3*df.values.std())]
        fig = Figure()
        ax = fig.subplots()
        ax.autoscale()
        ax.plot(df.index, df.values)
        if sensor.depth != 0:
            ax.set_title(f"{sensor.name} at depth of {sensor.depth:.2f} metres")
        else:
            ax.set_title(f"{sensor.name}")
        ax.tick_params(axis='x', labelrotation=30)
        # Save it to a temporary buffer.
        buf = BytesIO()
        fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        plots.append(data)
    return plots

app = Flask(__name__)

@app.before_request
def init_db():
    app.before_request_funcs[None].remove(init_db)
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_db(e):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    return render_template("index.html") 

@app.route("/upload-form")
def upload_form():
    return render_template("upload_form.html") 

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'dataset' not in request.files:
        return "file not found", 400 
    file = request.files['dataset']
    try:
        device = unmarshal_device(file.stream.read())
    except Exception as e:
        print(f"unmarshal_device error: {e}")
        return "an error occured", 400

    try:
        dbconn = get_db()
        insert_device(dbconn, device)
    except Exception as e:
        print(f"insert_device error: {e}")
        return "an error occured", 400

    plots = get_plots(device)

    return render_template("device_stats.html", device=device, plots=plots), 200

@app.route("/dashboard/<int:id>")
def dashboard(id: int):
    try:
        dbconn = get_db()
        device = get_device_by_id(dbconn, id) 
    except Exception as e:
        print(f"get_device_by_id error: {e}")
        return "an error occured", 400

    plots = get_plots(device)

    return render_template("device_stats.html", device=device, plots=plots), 200


@app.route("/geo-markers")
def geo_markers():
    markers = []
    rows = query_db("SELECT id,latitude,longtitude FROM device")
    if rows == None:
        return "no markers found", 400
    for marker in rows:
        markers.append({"id":marker["id"],"latitude":marker["latitude"],"longtitude":marker["longtitude"]})
    return {
            "markers": markers
            }, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
