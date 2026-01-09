from flask import Flask, request, jsonify
import time, hashlib, json, os

app = Flask(__name__)

SECRET = os.getenv("SECRET", "CHANGE_THIS_SECRET")
KEYS_FILE = "keys.json"

def h(k):
    return hashlib.sha256((k + SECRET).encode()).hexdigest()

def load_keys():
    if not os.path.exists(KEYS_FILE):
        return {}
    with open(KEYS_FILE, "r") as f:
        return json.load(f)

def save_keys(data):
    with open(KEYS_FILE, "w") as f:
        json.dump(data, f)

@app.route("/check", methods=["GET"])
def check_key():
    key = request.args.get("key")
    uid = request.args.get("uid")

    if not key or not uid:
        return jsonify(ok=False)

    keys = load_keys()
    data = keys.get(h(key))

    if not data:
        return jsonify(ok=False)

    if data["uid"] != uid:
        return jsonify(ok=False)

    if time.time() > data["exp"]:
        return jsonify(ok=False)

    return jsonify(ok=True)

@app.route("/add", methods=["POST"])
def add_key():
    if request.headers.get("X-ADMIN") != SECRET:
        return jsonify(ok=False)

    body = request.json
    key = body["key"]
    uid = body["uid"]
    exp = body["exp"]

    keys = load_keys()
    keys[h(key)] = {"uid": uid, "exp": exp}
    save_keys(keys)

    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
