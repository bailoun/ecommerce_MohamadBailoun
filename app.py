from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2

app = Flask(__name__)

DB_NAME = "ecommerce_db"
DB_USER = "bailoun"
DB_PASSWORD = "Hellohello123"
DB_HOST = "localhost"
DB_PORT = "5432"


def get_db_connection():
    return psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


conn = get_db_connection()

cur = conn.cursor()

cur.execute(
    """CREATE TABLE IF NOT EXISTS customers (
        id SERIAL PRIMARY KEY,
        fullname VARCHAR(50) NOT NULL,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(50) NOT NULL,
        age INT,
        address TEXT,
        gender VARCHAR(1),
        marital_status BOOLEAN
    );"""
)

conn.commit()

cur.close()
conn.close()


@app.route("/customers", methods=["POST"])
def register_customer():
    """
    Registers a new customer. Validates that the username is unique and stores customer information.
    """
    try:
        data = request.json

        fullname = data.get("fullname")
        username = data.get("username")
        password = data.get("password")
        age = data.get("age")
        address = data.get("address")
        gender = data.get("gender")
        marital_status = data.get("marital_status")

        if not all([fullname, username, password]):
            return (
                jsonify({"error": "fullname, username, and password are required"}),
                400,
            )

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM customers WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            return jsonify({"error": "Username is already taken"}), 409

        cur.execute(
            """
            INSERT INTO customers (fullname, username, password, age, address, gender, marital_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (fullname, username, password, age, address, gender, marital_status),
        )
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"message": "Customer registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/customers/<username>", methods=["DELETE"])
def delete_customer(username):
    """
    Deletes a customer from the database by username.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM customers WHERE username = %s", (username,))
        customer = cur.fetchone()

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        cur.execute("DELETE FROM customers WHERE username = %s", (username,))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"message": f"Customer '{username}' deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/customers/<username>", methods=["PUT"])
def update_customer(username):
    """
    Updates one or more fields for a customer based on the provided username.
    """
    try:
        data = request.json

        allowed_fields = {
            "fullname",
            "password",
            "age",
            "address",
            "gender",
            "marital_status",
        }
        update_fields = {
            key: value for key, value in data.items() if key in allowed_fields
        }

        if not update_fields:
            return jsonify({"error": "No valid fields provided for update"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM customers WHERE username = %s", (username,))
        customer = cur.fetchone()

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        set_clause = ", ".join([f"{field} = %s" for field in update_fields.keys()])
        values = list(update_fields.values())
        values.append(username)

        query = f"UPDATE customers SET {set_clause} WHERE username = %s"
        cur.execute(query, values)
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"message": f"Customer '{username}' updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/customers", methods=["GET"])
def get_all_customers():
    """
    Gets all customers and their information.
    """
    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute("""SELECT * FROM customers""")

    data = cur.fetchall()

    cur.close()
    conn.close()

    customers = [
        {
            "id": row[0],
            "fullname": row[1],
            "username": row[2],
            "password": row[3],
            "age": row[4],
            "address": row[5],
            "gender": row[6],
            "marital_status": row[7],
        }
        for row in data
    ]

    return jsonify(customers), 200


@app.route("/customers/<username>", methods=["GET"])
def get_customer_by_username(username):
    """
    Retrieves a customer by their unique username.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM customers WHERE username = %s", (username,))
        row = cur.fetchone()

        cur.close()
        conn.close()

        if not row:
            return jsonify({"error": "Customer not found"}), 404

        customer = {
            "id": row[0],
            "fullname": row[1],
            "username": row[2],
            "password": row[3],
            "age": row[4],
            "address": row[5],
            "gender": row[6],
            "marital_status": row[7],
        }

        return jsonify(customer), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/customers/<username>/charge", methods=["POST"])
def charge_customer_wallet(username):
    """
    Charges a customer's wallet in dollars.
    """
    try:
        data = request.json
        amount = data.get("amount")

        if not amount or not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify({"error": "Invalid amount. Must be a positive number."}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT wallet_balance FROM customers WHERE username = %s", (username,)
        )
        customer = cur.fetchone()

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        current_balance = customer[0]
        new_balance = current_balance + amount

        cur.execute(
            "UPDATE customers SET wallet_balance = %s WHERE username = %s",
            (new_balance, username),
        )
        conn.commit()

        cur.close()
        conn.close()

        return (
            jsonify(
                {"message": f"Wallet charged successfully", "new_balance": new_balance}
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/customers/<username>/deduct", methods=["POST"])
def deduct_money_from_wallet(username):
    """
    Deducts money from a customer's wallet.
    """
    try:
        data = request.json
        amount = data.get("amount")

        if not amount or not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify({"error": "Invalid amount. Must be a positive number."}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT wallet_balance FROM customers WHERE username = %s", (username,)
        )
        customer = cur.fetchone()

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        current_balance = customer[0]
        if current_balance < amount:
            return jsonify({"error": "Insufficient funds"}), 400

        new_balance = current_balance - amount
        cur.execute(
            "UPDATE customers SET wallet_balance = %s WHERE username = %s",
            (new_balance, username),
        )
        conn.commit()

        cur.close()
        conn.close()

        return (
            jsonify(
                {"message": f"Amount deducted successfully", "new_balance": new_balance}
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
