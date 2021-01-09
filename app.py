# -*- coding:utf-8 -*-
from flask import Flask, render_template

app = Flask("GamePatchBot")


@app.route("/")
def index():
    return render_template("index.html")


app.run()