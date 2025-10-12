from flask import Flask, render_template
import sys

app = Flask(__name__)

@app.route("/")
def hello():
return "Hello my webpage!"

if __name__ == "__main__":
application.run(host='0.0.0.0', debug=True)
