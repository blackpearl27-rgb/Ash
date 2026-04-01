from flask import Flask, render_template, request, jsonify
import os
import json
import base64


import mysql.connector

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",   # XAMPP default is empty
    database="sign_language_ai"
)

cursor = db.cursor(buffered=True)



app = Flask(__name__)

DATA_FILE = "samples.json"
IMAGE_FOLDER = "static/word_images"

os.makedirs(IMAGE_FOLDER, exist_ok=True)

# create dataset file if not exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/save_samples", methods=["POST"])
def save_samples():

    data = request.json
    word = data["word"]
    sample = json.dumps(data["sample"])

    query = "INSERT INTO samples (word, sample) VALUES (%s, %s)"
    cursor.execute(query, (word, sample))
    db.commit()

    return jsonify({"status": "saved"})

@app.route("/load_samples")
def load_samples():

    cursor.execute("SELECT word, sample FROM samples")
    rows = cursor.fetchall()

    dataset = {}

    for word, sample in rows:
        if word not in dataset:
            dataset[word] = []

        dataset[word].append(json.loads(sample))

    return jsonify(dataset)


@app.route("/upload_word_image", methods=["POST"])
def upload():

    word = request.form["word"]
    img = request.form["image"]

    imgdata = base64.b64decode(img.split(",")[1])

    path = os.path.join(IMAGE_FOLDER, word + ".png")

    with open(path, "wb") as f:
        f.write(imgdata)

    return jsonify({"status": "uploaded"})


@app.route("/get_word_images")
def get_images():

    images = {}

    for f in os.listdir(IMAGE_FOLDER):
        word = f.split(".")[0]
        images[word] = "/static/word_images/" + f

    return jsonify(images)

@app.route("/save_model", methods=["POST"])
def save_model():

    data = request.json
    model_json = data["model"]
    weights = data["weights"]

    cursor.execute("DELETE FROM models")  # keep only latest model

    query = "INSERT INTO models (model_json, weights) VALUES (%s, %s)"
    cursor.execute(query, (model_json, weights))
    db.commit()

    return jsonify({"status": "model saved"})

@app.route("/load_model")
def load_model():

    cursor.execute("SELECT model_json, weights FROM models ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    if row:
        return jsonify({
            "model": row[0],
            "weights": row[1]
        })

    return jsonify({"status": "no model"})


if __name__ == "__main__":
    app.run(debug=True)