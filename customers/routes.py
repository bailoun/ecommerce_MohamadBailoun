from flask import Blueprint, request, jsonify
from common.db import get_db

customers_bp = Blueprint("customers", __name__)


@customers_bp.route("/customers", methods=["POST"])
def register_customer():
    """
    Registers a new customer. Validates that the username is unique and stores customer information.
    Returns a success message if registration is successful or an error message otherwise.
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
        wallet_balance = data.get("wallet_balance", 0)

        if not all([fullname, username, password]):
            return (
                jsonify({"error": "fullname, username, and password are required"}),
                400,
            )

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT id FROM customers WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            return jsonify({"error": "Username is already taken"}), 409

        cur.execute(
            """
            INSERT INTO customers (fullname, username, password, age, address, gender, marital_status, wallet_balance)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                fullname,
                username,
                password,
                age,
                address,
                gender,
                marital_status,
                wallet_balance,
            ),
        )
        conn.commit()

        cur.close()

        return jsonify({"message": "Customer registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/customers/<username>", methods=["DELETE"])
def delete_customer(username):
    """
    Deletes a customer from the database by username.
    Returns a success message if the deletion is successful, or an error message if the customer is not found.
    """
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT id FROM customers WHERE username = %s", (username,))
        customer = cur.fetchone()

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        cur.execute("DELETE FROM customers WHERE username = %s", (username,))
        conn.commit()

        cur.close()

        return jsonify({"message": f"Customer '{username}' deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/customers/<username>", methods=["PUT"])
def update_customer(username):
    """
    Updates one or more fields for a customer based on the provided username.
    Valid fields include fullname, password, age, address, gender, marital_status.
    Returns a success message if the update is successful or an error message if no valid fields are provided.
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

        conn = get_db()
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

        return jsonify({"message": f"Customer '{username}' updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/customers", methods=["GET"])
def get_all_customers():
    """
    Retrieves all customers and their information.
    Returns a list of all customers' details in JSON format or an error message if there is an issue fetching the data.
    """
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""SELECT * FROM customers""")
        data = cur.fetchall()

        cur.close()

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
                "wallet_balance": row[8],
            }
            for row in data
        ]

        return jsonify(customers), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/customers/<username>", methods=["GET"])
def get_customer_by_username(username):
    """
    Retrieves a customer by their unique username.
    Returns the customer’s information if found, or an error message if the customer does not exist.
    """
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM customers WHERE username = %s", (username,))
        row = cur.fetchone()

        cur.close()

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
            "wallet_balance": row[8],
        }

        return jsonify(customer), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/customers/<username>/charge", methods=["POST"])
def charge_customer_wallet(username):
    """
    Charges a customer's wallet with a specified amount.
    Validates that the amount is positive. Returns the new wallet balance or an error message if invalid.
    """
    try:
        data = request.json
        amount = data.get("amount")

        if not amount or not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify({"error": "Invalid amount. Must be a positive number."}), 400

        conn = get_db()
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

        return (
            jsonify(
                {"message": "Wallet charged successfully", "new_balance": new_balance}
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/customers/<username>/deduct", methods=["POST"])
def deduct_money_from_wallet(username):
    """
    Deducts money from a customer's wallet.
    Ensures the amount is positive and that the customer has sufficient funds. Returns the new balance or an error message if there are insufficient funds.
    """
    try:
        data = request.json
        amount = data.get("amount")

        if not amount or not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify({"error": "Invalid amount. Must be a positive number."}), 400

        conn = get_db()
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

        return (
            jsonify(
                {"message": "Amount deducted successfully", "new_balance": new_balance}
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
