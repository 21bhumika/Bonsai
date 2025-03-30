from flask import Flask, send_file, jsonify, Response
import subprocess
import os
import random
from flask_cors import CORS
import time
import subprocess

app = Flask(__name__)
CORS(app)

@app.route("/run-main")
def run_main():
    def generate():
        process = subprocess.Popen(
            ["python", "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        for line in process.stdout:
            print(line.strip())  # Log for debugging
            if "Tree rendered to pics/" in line:
                filename = line.strip().split("Tree rendered to pics/")[-1]
                yield f"data: {filename}\n\n"
        process.stdout.close()
        process.wait()

    return Response(generate(), mimetype="text/event-stream")


@app.route("/output/<filename>")
def get_output(filename):
    return send_file(f"./pics/{filename}", mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)