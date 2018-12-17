from flask import Flask
from flask import render_template
from flask import url_for
from lift.api import api

app = Flask("lifting app")
app.register_blueprint(api)


@app.route("/", methods=["GET", "POST"])
def login():
    return render_template("index.html")
