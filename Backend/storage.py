import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USER_FILE = os.path.join(BASE_DIR, "users.csv")
SEEDS_FILE = os.path.join(BASE_DIR, "seeds.csv")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.csv")


def _ensure_file(path, header_row):
    if not os.path.exists(path):
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header_row)


# Ensure files exist with a default admin user
_ensure_file(USER_FILE, ["username", "password", "role"])
# create admin if not present
if True:
    exists = False
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", newline="") as f:
            reader = csv.DictReader(f)
            for r in reader:
                if r.get("username") == "admin":
                    exists = True
                    break
    if not exists:
        with open(USER_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["admin", "1234", "admin"])

_ensure_file(SEEDS_FILE, ["id", "name", "price"])
# create example seed if empty
if os.path.getsize(SEEDS_FILE) == 0 or sum(1 for _ in open(SEEDS_FILE)) <= 1:
    with open(SEEDS_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([1, "Wheat", "120.00"])
        writer.writerow([2, "Corn", "75.50"])

_ensure_file(FEEDBACK_FILE, ["user", "comment"])


# -------------------------
# Users
# -------------------------
def check_login(username, password):
    username = (username or "").strip()
    password = (password or "").strip()
    with open(USER_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("username") == username and row.get("password") == password:
                return True
    return False


def add_user(username, password):
    username = (username or "").strip()
    password = (password or "").strip()
    if not username or not password:
        return False
    with open(USER_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("username") == username:
                return False
    with open(USER_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([username, password, "user"])
    return True


def get_all_users():
    users = []
    with open(USER_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append({"username": row.get("username"), "role": row.get("role", "user")})
    return users


# -------------------------
# Seeds CRUD
# -------------------------
def get_seeds():
    seeds = []
    with open(SEEDS_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                sid = int(row.get("id"))
            except Exception:
                sid = None
            name = row.get("name")
            try:
                price = float(row.get("price"))
            except Exception:
                price = row.get("price")
            seeds.append({"id": sid, "name": name, "price": price})
    return seeds


def add_seed(seed_data):
    if seed_data is None or "id" not in seed_data or "name" not in seed_data:
        return False
    sid = int(seed_data["id"])
    for s in get_seeds():
        if s["id"] == sid:
            return False
    with open(SEEDS_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([sid, seed_data["name"], str(seed_data.get("price", ""))])
    return True


def update_seed(seed_id, updated_data):
    seed_id = int(seed_id)
    rows = []
    found = False
    with open(SEEDS_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row.get("id")) == seed_id:
                row["name"] = updated_data.get("name", row.get("name"))
                row["price"] = str(updated_data.get("price", row.get("price")))
                found = True
            rows.append(row)
    if not found:
        return False
    with open(SEEDS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "price"])
        writer.writeheader()
        for r in rows:
            writer.writerow([r["id"], r["name"], r["price"]])
    return True


def delete_seed(seed_id):
    seed_id = int(seed_id)
    rows = []
    found = False
    with open(SEEDS_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row.get("id")) == seed_id:
                found = True
                continue
            rows.append(row)
    if not found:
        return False
    with open(SEEDS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "price"])
        writer.writeheader()
        for r in rows:
            writer.writerow([r["id"], r["name"], r["price"]])
    return True


# -------------------------
# Feedback
# -------------------------
def add_feedback(feedback_data):
    if feedback_data is None or "user" not in feedback_data or "comment" not in feedback_data:
        return False

    # Ensure proper header & write as dict
    with open(FEEDBACK_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["user", "comment"])
        if os.path.getsize(FEEDBACK_FILE) == 0:  # file empty
            writer.writeheader()
        writer.writerow({"user": feedback_data["user"], "comment": feedback_data["comment"]})
    return True


def get_all_feedback():
    feedbacks = []
    with open(FEEDBACK_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("user") and row.get("comment"):  # skip empty rows
                feedbacks.append({"user": row.get("user"), "comment": row.get("comment")})
    return feedbacks
