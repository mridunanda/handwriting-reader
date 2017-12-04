import os
import re
from flask import Flask, jsonify, render_template, request
from vector_helpers import make_image, fuzzify, new_fuzzify
from bitmap_helpers import process
from recognize import recognize
from scipy import misc
# testing grid -MN
# from train import train_testMN

# Configure application
app = Flask(__name__)


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
    # Our algorithm here
    path = request.form.get("draw")
    image = make_image(path)
    character = recognize(new_fuzzify(image))
    #return render_template("recognize.html", character=character)
    return render_template("read.html", image=new_fuzzify(image), SIDE_LENGTH=28)
    
    # testing grid -MN
    # train_grid = train_testMN()
    # return render_template("read.html", image=train_grid, SIDE_LENGTH=28)


@app.route("/read-file", methods=["POST"])  
def read_file():
    # Our algorithm here
    file = request.files["file"]
    arr = misc.imread(file)
    image = process(arr)
    character = recognize(image)
    # return render_template("recognize.html", character=character)
    return render_template("read.html", image=image, SIDE_LENGTH=28)
    

# @app.route()
