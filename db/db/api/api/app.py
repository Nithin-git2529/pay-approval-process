from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "pay.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

app = Flask(__name__)
CORS(app)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db_if_needed():
    # Create tables if DB not present
    if not os.path.exists(DB_PATH):
        from pathlib import Path
        schema_file = Path(__file__).parent.parent / "db" / "schema.sql"
        seed_file = Path(__file__).parent.parent / "db" / "seed.sql"
        conn = get_conn()
        with open(schema_file, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        with open(seed_file, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()

@app.route("/request", methods=["POST"])
def create_request():
    data = request.get_json(force=True)
    employee_id = data.get("employee_id")
    amount = data.get("amount")
    reason = data.get("reason", "")

    if not employee_id or not amount:
        return jsonify({"error": "employee_id and amount are required"}), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO requests(employee_id, amount, reason, status, created_at, updated_at)
        VALUES (?, ?, ?, 'PENDING', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (employee_id, amount, reason))
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return jsonify({"message": "request created", "request_id": rid}), 201

@app.route("/requests", methods=["GET"])
def list_requests():
    conn = get_conn()
    rows = conn.execute("""
        SELECT r.id, r.employee_id, e.name as employee_name, r.amount, r.reason,
               r.status, r.created_at, r.updated_at
        FROM requests r
        JOIN employees e ON e.id = r.employee_id
        ORDER BY r.created_at DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/approve", methods=["POST"])
def approve():
    data = request.get_json(force=True)
    request_id = data.get("request_id")
    manager_id = data.get("manager_id")
    if not request_id or not manager_id:
        return jsonify({"error": "request_id and manager_id required"}), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO approvals(request_id, manager_id, action) VALUES (?, ?, 'APPROVE')",
                (request_id, manager_id))
    cur.execute("UPDATE requests SET status='APPROVED', updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (request_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "approved"}), 200

@app.route("/reject", methods=["POST"])
def reject():
    data = request.get_json(force=True)
    request_id = data.get("request_id")
    manager_id = data.get("manager_id")
    reason = data.get("reason", "")
    if not request_id or not manager_id:
        return jsonify({"error": "request_id and manager_id required"}), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO approvals(request_id, manager_id, action, reason) VALUES (?, ?, 'REJECT', ?)",
                (request_id, manager_id, reason))
    cur.execute("UPDATE requests SET status='REJECTED', updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (request_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "rejected"}), 200

@app.route("/")
def health():
    return jsonify({"service": "pay-approval-process", "status": "ok"})

if __name__ == "__main__":
    init_db_if_needed()
    app.run(debug=True)
