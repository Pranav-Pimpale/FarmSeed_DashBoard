from flask import Flask, request, jsonify
from flask_cors import CORS
from storage import (
    check_login, add_user, get_all_users,
    get_seeds, add_seed, update_seed, delete_seed,
    add_feedback
)
from logger import log_request, log_data

app = Flask(__name__)
CORS(app)  # allow requests from Streamlit frontend

# -------------------------
# Login Route
# -------------------------
@app.route("/login", methods=["POST"])
@log_request
def login():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    # Admin hardcoded
    if username == "admin" and password == "1234":
        return jsonify({"status": "success", "role": "admin"}), 200

    # Normal user check
    if check_login(username, password):
        return jsonify({"status": "success", "role": "user"}), 200

    return jsonify({"status": "failed"}), 401


# -------------------------
# Register User
# -------------------------
@app.route("/register", methods=["POST"])
@log_request
def register():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jsonify({"status": "failed", "message": "Missing username or password"}), 400
    if add_user(username, password):
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "failed", "message": "User already exists"}), 409


# -------------------------
# Users listing (admin)
# -------------------------
@app.route("/users", methods=["GET"])
@log_request
def list_users():
    return jsonify({"users": get_all_users()}), 200


# -------------------------
# Seeds CRUD (frontend expects these)
# Note: current frontend does not send auth credentials for seed actions.
# If you want to enforce admin-only on these endpoints, require credentials
# in the request JSON and check them here (comment says where).
# -------------------------
@app.route("/seeds", methods=["GET"])
@log_request
@log_data
def seeds_list():
    return jsonify(get_seeds()), 200


@app.route("/seeds", methods=["POST"])
@log_request
def create_seed():
    data = request.json or {}
    seed = data  # front-end sends new_seed like {"id":..., "name":..., "price":...}

    # --- Optional admin enforcement (uncomment to enable) ---
    # if not (data.get("username") == "admin" and data.get("password") == "1234"):
    #     return jsonify({"status":"forbidden"}), 403

    if add_seed(seed):
        return jsonify({"status": "Seed added"}), 201
    return jsonify({"status": "error", "message": "Could not add seed (duplicate id?)."}), 400


@app.route("/seeds/<int:seed_id>", methods=["PUT"])
@log_request
def edit_seed(seed_id):
    data = request.json or {}
    updated = data  # front-end sends {"name":..., "price":...}

    # Optional enforce admin:
    # if not (data.get("username") == "admin" and data.get("password") == "1234"):
    #     return jsonify({"status":"forbidden"}), 403

    if update_seed(seed_id, updated):
        return jsonify({"status": "Seed updated"}), 200
    return jsonify({"status": "error", "message": "Seed not found"}), 404


@app.route("/seeds/<int:seed_id>", methods=["DELETE"])
@log_request
def remove_seed(seed_id):
    data = request.json or {}

    # Optional enforce admin:
    # if not (data.get("username") == "admin" and data.get("password") == "1234"):
    #     return jsonify({"status":"forbidden"}), 403

    if delete_seed(seed_id):
        return jsonify({"status": "Seed deleted"}), 200
    return jsonify({"status": "error", "message": "Seed not found"}), 404
from flask import Flask, request, jsonify
from flask_cors import CORS
from storage import (
    check_login, add_user, get_all_users,
    get_seeds, add_seed, update_seed, delete_seed,
    add_feedback, get_all_feedback
)
from logger import log_request, log_data

app = Flask(__name__)
CORS(app)

# -------------------------
# Login Route
# -------------------------
@app.route("/login", methods=["POST"])
@log_request
def login():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if username == "admin" and password == "1234":
        return jsonify({"status": "success", "role": "admin"}), 200

    if check_login(username, password):
        return jsonify({"status": "success", "role": "user"}), 200

    return jsonify({"status": "failed"}), 401


# -------------------------
# Register User
# -------------------------
@app.route("/register", methods=["POST"])
@log_request
def register():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jsonify({"status": "failed", "message": "Missing username or password"}), 400
    if add_user(username, password):
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "failed", "message": "User already exists"}), 409


# -------------------------
# Users listing (admin)
# -------------------------
@app.route("/users", methods=["GET"])
@log_request
def list_users():
    return jsonify({"users": get_all_users()}), 200


# -------------------------
# Seeds CRUD
# -------------------------
@app.route("/seeds", methods=["GET"])
@log_request
@log_data
def seeds_list():
    return jsonify(get_seeds()), 200


@app.route("/seeds", methods=["POST"])
@log_request
def create_seed():
    data = request.json or {}
    seed = data
    if add_seed(seed):
        return jsonify({"status": "Seed added"}), 201
    return jsonify({"status": "error", "message": "Could not add seed (duplicate id?)."}), 400


@app.route("/seeds/<int:seed_id>", methods=["PUT"])
@log_request
def edit_seed(seed_id):
    data = request.json or {}
    updated = data
    if update_seed(seed_id, updated):
        return jsonify({"status": "Seed updated"}), 200
    return jsonify({"status": "error", "message": "Seed not found"}), 404


@app.route("/seeds/<int:seed_id>", methods=["DELETE"])
@log_request
def remove_seed(seed_id):
    if delete_seed(seed_id):
        return jsonify({"status": "Seed deleted"}), 200
    return jsonify({"status": "error", "message": "Seed not found"}), 404


# -------------------------
# Feedback endpoints
# -------------------------
@app.route("/feedback", methods=["POST"])
@log_request
def feedback():
    data = request.json or {}
    if add_feedback(data):
        return jsonify({"status": "Feedback added"}), 200
    return jsonify({"status": "error", "message": "Invalid feedback payload"}), 400


@app.route("/feedbacks", methods=["GET"])
@log_request
def feedbacks_list():
    username = request.args.get("username")
    password = request.args.get("password")
    if not (username == "admin" and password == "1234"):
        return jsonify({"status": "forbidden"}), 403
    return jsonify(get_all_feedback()), 200


if __name__ == "__main__":
    app.run(debug=True)



# -------------------------
# Feedback endpoint (all users)
# -------------------------
@app.route("/feedback", methods=["POST"])
@log_request
def feedback():
    data = request.json or {}
    if add_feedback(data):
        return jsonify({"status": "Feedback added"}), 200
    return jsonify({"status": "error", "message": "Invalid feedback payload"}), 400


if __name__ == "__main__":
    app.run(debug=True)  