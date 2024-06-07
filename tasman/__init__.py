from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("upload_form.html") 

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return "file not found", 400 

    file = request.files['file']
    print(file.stream.read())
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
