import os
import re
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from vector_helpers import make_image, blur
from bitmap_helpers import process
from recognize import recognize, re_learn
from scipy import misc
import numpy as np

# Configure application
app = Flask(__name__)
app.secret_key = "secrets"

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
  return render_template("index.html")
  
@app.route("/read-vector", methods=["POST"])  
def read_vector():
    path = request.form.get("draw")
    image = make_image(path)
    character = recognize(blur(image))
    session["image"] = image.tolist()
    session["character"] = character
    global_image_store = blur(image)
    return render_template("recognize.html", character=character)
    # return render_template("read.html", image=blur(image), SIDE_LENGTH=28)

@app.route("/read-file", methods=["POST"])  
def read_file():
    file = request.files["file"]
    arr = misc.imread(file)
    image = process(arr)
    character = recognize(image)
    session["image"] = image.tolist()
    session["character"] = character
    return render_template("recognize.html", character=character)
    # return render_template("read.html", image=image, SIDE_LENGTH=28)

@app.route("/learn", methods=["POST"])
def learn():
    correct = True if request.form.get("yes") == "on" else False
    should_be = int(request.form.get("num")) if not correct else session["character"]
    if not(should_be in range(10)):
        return redirect(url_for("index"))
    re_learn(np.array(session["image"]), should_be)
    return redirect(url_for("index"))


