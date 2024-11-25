from flask import Blueprint, request, jsonify
from common.db import get_db

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.route("/inventory", methods=["POST"])
def add_goods():
    """
    Add goods to the inventory. Validates category, price, and count of items in stock.
    """
    try:
        data = request.json

        name = data.get("name")
        category = data.get("category")
        price_per_item = data.get("price_per_item")
        description = data.get("description")
        count_in_stock = data.get("count_in_stock")

        if not name or not category or price_per_item is None or count_in_stock is None:
            return jsonify({"error": "Missing required fields"}), 400

        if category not in ["food", "clothes", "accessories", "electronics"]:
            return jsonify({"error": "Invalid category"}), 400

        if price_per_item < 0:
            return (
                jsonify({"error": "Price and count_in_stock must be non-negative"}),
                400,
            )

        if count_in_stock < 0:
            return (
                jsonify({"error: Count of items in stock must be non-negative"}),
                400,
            )

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO inventory (name, category, price_per_item, description, count_in_stock)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (name, category, price_per_item, description, count_in_stock),
        )
        item_id = cur.fetchone()[0]
        conn.commit()
        cur.close()

        return jsonify({"message": "Item added successfully", "id": item_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@inventory_bp.route("/inventory/<int:item_id>/deduct", methods=["PATCH"])
def deduct_goods(item_id):
    """
    Deduct a specified quantity of goods from stock.
    """
    try:
        data = request.json
        quantity = data.get("quantity")

        if quantity is None or quantity <= 0:
            return jsonify({"error": "Invalid quantity"}), 400

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT count_in_stock FROM inventory WHERE id = %s", (item_id,))
        item = cur.fetchone()

        if not item:
            return jsonify({"error": "Item not found"}), 404

        current_stock = item[0]

        if current_stock < quantity:
            return jsonify({"error": "Not enough stock available"}), 400

        cur.execute(
            "UPDATE inventory SET count_in_stock = count_in_stock - %s WHERE id = %s",
            (quantity, item_id),
        )
        conn.commit()
        cur.close()

        return jsonify({"message": "Stock deducted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@inventory_bp.route("/inventory/<int:item_id>", methods=["PUT"])
def update_goods(item_id):
    """
    Update fields related to a specific item in the inventory.
    """
    try:
        data = request.json

        updates = []
        values = []

        for field in [
            "name",
            "category",
            "price_per_item",
            "description",
            "count_in_stock",
        ]:
            if field in data:
                updates.append(f"{field} = %s")
                values.append(data[field])

        if "category" in data and data["category"] not in [
            "food",
            "clothes",
            "accessories",
            "electronics",
        ]:
            return jsonify({"error": "Invalid category"}), 400

        if "price_per_item" in data and data["price_per_item"] < 0:
            return jsonify({"error": "Price must be non-negative"}), 400
        if "count_in_stock" in data and data["count_in_stock"] < 0:
            return jsonify({"error": "Count in stock must be non-negative"}), 400

        if not updates:
            return jsonify({"error": "No fields to update"}), 400

        values.append(item_id)

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            f"""
            UPDATE inventory
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id
            """,
            values,
        )
        updated_item_id = cur.fetchone()

        if not updated_item_id:
            return jsonify({"error": "Item not found"}), 404

        conn.commit()
        cur.close()

        return (
            jsonify({"message": "Item updated successfully", "id": updated_item_id[0]}),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
