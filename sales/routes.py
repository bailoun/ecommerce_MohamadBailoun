from flask import Blueprint, request, jsonify
from common.db import get_db

sales_bp = Blueprint("sales", __name__)


@sales_bp.route("/sales/goods", methods=["GET"])
def display_available_goods():
    """
    Returns a list of available goods with their name and price.
    Filters out items with zero stock and only includes those with available quantity.
    """
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, name, price_per_item
            FROM inventory
            WHERE count_in_stock > 0
        """
        )
        goods = cur.fetchall()
        cur.close()

        goods_list = [
            {"id": row[0], "name": row[1], "price_per_item": float(row[2])}
            for row in goods
        ]

        return jsonify(goods_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sales_bp.route("/sales/goods/<int:item_id>", methods=["GET"])
def get_good_details(item_id):
    """
    Returns full information related to a specific good by item_id.
    Retrieves details including the name, category, price, description, and stock count.
    """
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, name, category, price_per_item, description, count_in_stock
            FROM inventory
            WHERE id = %s
        """,
            (item_id,),
        )
        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({"error": "Item not found"}), 404

        item = {
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "price_per_item": float(row[3]),
            "description": row[4],
            "count_in_stock": row[5],
        }

        return jsonify(item), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sales_bp.route("/sales/purchase", methods=["POST"])
def make_purchase():
    """
    Processes a sale where a customer purchases an item.
    Checks for sufficient stock, customer funds, and updates both wallet and inventory accordingly.
    """
    try:
        data = request.json

        username = data.get("username")
        item_id = data.get("item_id")
        quantity = data.get("quantity")

        if not username or not item_id or not quantity:
            return (
                jsonify({"error": "username, item_id, and quantity are required"}),
                400,
            )

        if quantity <= 0:
            return jsonify({"error": "Quantity must be positive"}), 400

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, wallet_balance FROM customers WHERE username = %s", (username,)
        )
        customer = cur.fetchone()
        if not customer:
            cur.close()
            return jsonify({"error": "Customer not found"}), 404
        customer_id = customer[0]
        wallet_balance = float(customer[1])

        cur.execute(
            "SELECT id, price_per_item, count_in_stock FROM inventory WHERE id = %s",
            (item_id,),
        )
        item = cur.fetchone()
        if not item:
            cur.close()
            return jsonify({"error": "Item not found"}), 404
        item_id = item[0]
        price_per_item = float(item[1])
        count_in_stock = item[2]

        if count_in_stock < quantity:
            cur.close()
            return jsonify({"error": "Not enough stock available"}), 400

        total_price = price_per_item * quantity

        if wallet_balance < total_price:
            cur.close()
            return jsonify({"error": "Insufficient funds"}), 400

        new_wallet_balance = wallet_balance - total_price
        cur.execute(
            "UPDATE customers SET wallet_balance = %s WHERE id = %s",
            (new_wallet_balance, customer_id),
        )

        new_count_in_stock = count_in_stock - quantity
        cur.execute(
            "UPDATE inventory SET count_in_stock = %s WHERE id = %s",
            (new_count_in_stock, item_id),
        )

        cur.execute(
            """
            INSERT INTO sales (customer_id, item_id, quantity)
            VALUES (%s, %s, %s)
            """,
            (customer_id, item_id, quantity),
        )

        conn.commit()
        cur.close()

        return jsonify({"message": "Purchase successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sales_bp.route("/sales/customers/<username>/purchases", methods=["GET"])
def get_customer_purchases(username):
    """
    Returns all historical purchases made by a specific customer.
    Retrieves a list of all past purchases including item details, quantity, and sale date.
    """
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT id FROM customers WHERE username = %s", (username,))
        customer = cur.fetchone()
        if not customer:
            cur.close()
            return jsonify({"error": "Customer not found"}), 404
        customer_id = customer[0]

        cur.execute(
            """
            SELECT sales.id, sales.quantity, sales.sale_date,
                   inventory.id AS item_id, inventory.name, inventory.price_per_item
            FROM sales
            JOIN inventory ON sales.item_id = inventory.id
            WHERE sales.customer_id = %s
            ORDER BY sales.sale_date DESC
        """,
            (customer_id,),
        )
        purchases = cur.fetchall()
        cur.close()

        purchases_list = [
            {
                "sale_id": row[0],
                "quantity": row[1],
                "sale_date": row[2].isoformat(),
                "item": {"id": row[3], "name": row[4], "price_per_item": float(row[5])},
            }
            for row in purchases
        ]

        return jsonify(purchases_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
