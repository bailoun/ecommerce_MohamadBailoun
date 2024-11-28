# reviews/routes.py
from flask import Blueprint, request, jsonify
from common.db import get_db

reviews_bp = Blueprint("reviews", __name__)


@reviews_bp.route("/reviews", methods=["POST"])
def submit_review():
    """
    Allows customers to submit a review for a specific product.
    """
    try:
        data = request.json

        username = data.get("username")
        item_id = data.get("item_id")
        rating = data.get("rating")
        comment = data.get("comment", "")

        if not username or not item_id or not rating:
            return jsonify({"error": "username, item_id, and rating are required"}), 400

        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400

        conn = get_db()
        cur = conn.cursor()

        # Get customer_id
        cur.execute("SELECT id FROM customers WHERE username = %s", (username,))
        customer = cur.fetchone()
        if not customer:
            cur.close()
            return jsonify({"error": "Customer not found"}), 404
        customer_id = customer[0]

        # Check if item exists
        cur.execute("SELECT id FROM inventory WHERE id = %s", (item_id,))
        item = cur.fetchone()
        if not item:
            cur.close()
            return jsonify({"error": "Item not found"}), 404

        # Insert review
        cur.execute(
            """
            INSERT INTO reviews (customer_id, item_id, rating, comment)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (customer_id, item_id, rating, comment),
        )
        review_id = cur.fetchone()[0]
        conn.commit()
        cur.close()

        return (
            jsonify(
                {"message": "Review submitted successfully", "review_id": review_id}
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reviews_bp.route("/reviews/<int:review_id>", methods=["PUT"])
def update_review(review_id):
    """
    Allows customers to update their existing review.
    """
    try:
        data = request.json

        username = data.get("username")
        rating = data.get("rating")
        comment = data.get("comment", "")

        if not username or (rating is None and not comment):
            return (
                jsonify(
                    {
                        "error": "username and at least one of rating or comment are required"
                    }
                ),
                400,
            )

        if rating is not None and (rating < 1 or rating > 5):
            return jsonify({"error": "Rating must be between 1 and 5"}), 400

        conn = get_db()
        cur = conn.cursor()

        # Get customer_id
        cur.execute("SELECT id FROM customers WHERE username = %s", (username,))
        customer = cur.fetchone()
        if not customer:
            cur.close()
            return jsonify({"error": "Customer not found"}), 404
        customer_id = customer[0]

        # Check if review exists and belongs to the customer
        cur.execute("SELECT customer_id FROM reviews WHERE id = %s", (review_id,))
        review = cur.fetchone()
        if not review:
            cur.close()
            return jsonify({"error": "Review not found"}), 404
        if review[0] != customer_id:
            cur.close()
            return jsonify({"error": "Unauthorized action"}), 403

        # Update review
        fields = []
        values = []

        if rating is not None:
            fields.append("rating = %s")
            values.append(rating)
        if comment:
            fields.append("comment = %s")
            values.append(comment)

        values.append(review_id)
        cur.execute(
            f"""
            UPDATE reviews
            SET {', '.join(fields)}
            WHERE id = %s
            """,
            values,
        )
        conn.commit()
        cur.close()

        return jsonify({"message": "Review updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reviews_bp.route("/reviews/<int:review_id>", methods=["DELETE"])
def delete_review(review_id):
    """
    Allows customers to delete their own review.
    """
    try:
        data = request.json
        username = data.get("username")

        if not username:
            return jsonify({"error": "username is required"}), 400

        conn = get_db()
        cur = conn.cursor()

        # Get customer_id
        cur.execute("SELECT id FROM customers WHERE username = %s", (username,))
        customer = cur.fetchone()
        if not customer:
            cur.close()
            return jsonify({"error": "Customer not found"}), 404
        customer_id = customer[0]

        # Check if review exists and belongs to the customer
        cur.execute("SELECT customer_id FROM reviews WHERE id = %s", (review_id,))
        review = cur.fetchone()
        if not review:
            cur.close()
            return jsonify({"error": "Review not found"}), 404
        if review[0] != customer_id:
            cur.close()
            return jsonify({"error": "Unauthorized action"}), 403

        # Delete review
        cur.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
        conn.commit()
        cur.close()

        return jsonify({"message": "Review deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reviews_bp.route("/reviews/product/<int:item_id>", methods=["GET"])
def get_product_reviews(item_id):
    """
    Retrieves all approved reviews for a specific product.
    """
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT reviews.id, customers.username, reviews.rating, reviews.comment, reviews.review_date
            FROM reviews
            JOIN customers ON reviews.customer_id = customers.id
            WHERE reviews.item_id = %s AND reviews.is_approved = TRUE
            ORDER BY reviews.review_date DESC
        """,
            (item_id,),
        )
        reviews = cur.fetchall()
        cur.close()

        reviews_list = [
            {
                "review_id": row[0],
                "username": row[1],
                "rating": row[2],
                "comment": row[3],
                "review_date": row[4].isoformat(),
            }
            for row in reviews
        ]

        return jsonify(reviews_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reviews_bp.route("/reviews/customer/<username>", methods=["GET"])
def get_customer_reviews(username):
    """
    Lists all reviews submitted by a specific customer.
    """
    try:
        conn = get_db()
        cur = conn.cursor()

        # Get customer_id
        cur.execute("SELECT id FROM customers WHERE username = %s", (username,))
        customer = cur.fetchone()
        if not customer:
            cur.close()
            return jsonify({"error": "Customer not found"}), 404
        customer_id = customer[0]

        cur.execute(
            """
            SELECT reviews.id, inventory.name, reviews.rating, reviews.comment, reviews.review_date, reviews.is_approved
            FROM reviews
            JOIN inventory ON reviews.item_id = inventory.id
            WHERE reviews.customer_id = %s
            ORDER BY reviews.review_date DESC
        """,
            (customer_id,),
        )
        reviews = cur.fetchall()
        cur.close()

        reviews_list = [
            {
                "review_id": row[0],
                "product_name": row[1],
                "rating": row[2],
                "comment": row[3],
                "review_date": row[4].isoformat(),
                "is_approved": row[5],
            }
            for row in reviews
        ]

        return jsonify(reviews_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reviews_bp.route("/reviews/<int:review_id>/moderate", methods=["PATCH"])
def moderate_review(review_id):
    """
    Allows administrators to approve or flag reviews.
    """
    try:
        data = request.json
        is_approved = data.get("is_approved")

        if is_approved is None:
            return jsonify({"error": "is_approved is required"}), 400

        # Here, you might implement authentication to check if the requester is an admin.
        # For simplicity, we'll assume the requester is an admin.

        conn = get_db()
        cur = conn.cursor()

        # Check if review exists
        cur.execute("SELECT id FROM reviews WHERE id = %s", (review_id,))
        review = cur.fetchone()
        if not review:
            cur.close()
            return jsonify({"error": "Review not found"}), 404

        # Update is_approved status
        cur.execute(
            "UPDATE reviews SET is_approved = %s WHERE id = %s",
            (is_approved, review_id),
        )
        conn.commit()
        cur.close()

        return jsonify({"message": "Review moderation updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reviews_bp.route("/reviews/<int:review_id>", methods=["GET"])
def get_review_details(review_id):
    """
    Provides detailed information about a specific review.
    """
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT reviews.id, customers.username, inventory.name, reviews.rating, reviews.comment, reviews.review_date, reviews.is_approved
            FROM reviews
            JOIN customers ON reviews.customer_id = customers.id
            JOIN inventory ON reviews.item_id = inventory.id
            WHERE reviews.id = %s
        """,
            (review_id,),
        )
        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({"error": "Review not found"}), 404

        review = {
            "review_id": row[0],
            "username": row[1],
            "product_name": row[2],
            "rating": row[3],
            "comment": row[4],
            "review_date": row[5].isoformat(),
            "is_approved": row[6],
        }

        return jsonify(review), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
