import pandas as pd
from matplotlib.figure import Figure
from tasman.unmarshal import unmarshal_device
from tasman.model import Observation
from tasman.db import get_db, insert_device
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
def home():
    return render_template("upload_form.html") 

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return "file not found", 400 
    file = request.files['file']
    device = unmarshal_device(file.stream.read())
    dbconn = get_db()
    insert_device(dbconn, device)

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
