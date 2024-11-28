def test_submit_review(client):
    client.post(
        "/customers",
        json={
            "fullname": "Grace Hopper",
            "username": "ghopper",
            "password": "password123",
        },
    )
    response = client.post(
        "/inventory",
        json={
            "name": "USB Cable",
            "category": "electronics",
            "price_per_item": 5.99,
            "count_in_stock": 100,
        },
    )
    item_id = response.get_json()["id"]
    response = client.post(
        "/reviews",
        json={
            "username": "ghopper",
            "item_id": item_id,
            "rating": 5,
            "comment": "Excellent quality!",
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Review submitted successfully"
    assert "review_id" in data

    response = client.post("/reviews", json={"username": "ghopper", "item_id": item_id})
    assert response.status_code == 400
    assert "username, item_id, and rating are required" in response.get_json()["error"]


def test_update_review(client):
    client.post(
        "/customers",
        json={
            "fullname": "Ada Lovelace",
            "username": "alovelace",
            "password": "password123",
        },
    )
    response = client.post(
        "/inventory",
        json={
            "name": "Keyboard",
            "category": "electronics",
            "price_per_item": 49.99,
            "count_in_stock": 50,
        },
    )
    item_id = response.get_json()["id"]
    response = client.post(
        "/reviews",
        json={
            "username": "alovelace",
            "item_id": item_id,
            "rating": 4,
            "comment": "Good keyboard.",
        },
    )
    review_id = response.get_json()["review_id"]
    response = client.put(
        f"/reviews/{review_id}",
        json={"username": "alovelace", "rating": 5, "comment": "Great keyboard!"},
    )
    assert response.status_code == 200
    assert response.get_json()["message"] == "Review updated successfully"
    response = client.put(
        f"/reviews/{review_id}", json={"username": "alovelace", "rating": 6}
    )
    assert response.status_code == 400
    assert "Rating must be between 1 and 5" in response.get_json()["error"]
    # Unauthorized update attempt
    response = client.put(
        f"/reviews/{review_id}", json={"username": "someoneelse", "rating": 3}
    )
    assert response.status_code == 404


def test_delete_review(client):
    client.post(
        "/customers",
        json={
            "fullname": "Linus Torvalds",
            "username": "ltorvalds",
            "password": "password123",
        },
    )
    response = client.post(
        "/inventory",
        json={
            "name": "Monitor",
            "category": "electronics",
            "price_per_item": 199.99,
            "count_in_stock": 20,
        },
    )
    item_id = response.get_json()["id"]
    response = client.post(
        "/reviews",
        json={
            "username": "ltorvalds",
            "item_id": item_id,
            "rating": 3,
            "comment": "Average monitor.",
        },
    )
    review_id = response.get_json()["review_id"]
    response = client.delete(f"/reviews/{review_id}", json={"username": "ltorvalds"})
    assert response.status_code == 200
    assert response.get_json()["message"] == "Review deleted successfully"
    response = client.get(f"/reviews/{review_id}")
    assert response.status_code == 404


def test_get_product_reviews(client):
    client.post(
        "/customers",
        json={
            "fullname": "Alan Turing",
            "username": "aturing",
            "password": "password123",
        },
    )
    client.post(
        "/customers",
        json={
            "fullname": "Katherine Johnson",
            "username": "kjohnson",
            "password": "password123",
        },
    )
    response = client.post(
        "/inventory",
        json={
            "name": "Laptop",
            "category": "electronics",
            "price_per_item": 999.99,
            "count_in_stock": 10,
        },
    )
    item_id = response.get_json()["id"]
    response = client.post(
        "/reviews",
        json={
            "username": "aturing",
            "item_id": item_id,
            "rating": 5,
            "comment": "Fantastic laptop!",
        },
    )
    review_id1 = response.get_json()["review_id"]
    response = client.post(
        "/reviews",
        json={
            "username": "kjohnson",
            "item_id": item_id,
            "rating": 4,
            "comment": "Very good performance.",
        },
    )
    review_id2 = response.get_json()["review_id"]
    client.patch(f"/reviews/{review_id1}/moderate", json={"is_approved": True})
    client.patch(f"/reviews/{review_id2}/moderate", json={"is_approved": True})
    response = client.get(f"/reviews/product/{item_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    usernames = [review["username"] for review in data]
    assert "aturing" in usernames
    assert "kjohnson" in usernames


def test_get_customer_reviews(client):
    client.post(
        "/customers",
        json={
            "fullname": "Margaret Hamilton",
            "username": "mhamilton",
            "password": "password123",
        },
    )
    response = client.post(
        "/inventory",
        json={
            "name": "Smartphone",
            "category": "electronics",
            "price_per_item": 799.99,
            "count_in_stock": 15,
        },
    )
    item_id1 = response.get_json()["id"]
    response = client.post(
        "/inventory",
        json={
            "name": "Tablet",
            "category": "electronics",
            "price_per_item": 499.99,
            "count_in_stock": 20,
        },
    )
    item_id2 = response.get_json()["id"]
    response = client.post(
        "/reviews",
        json={
            "username": "mhamilton",
            "item_id": item_id1,
            "rating": 4,
            "comment": "Good smartphone.",
        },
    )
    response = client.post(
        "/reviews",
        json={
            "username": "mhamilton",
            "item_id": item_id2,
            "rating": 5,
            "comment": "Excellent tablet.",
        },
    )
    response = client.get("/reviews/customer/mhamilton")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    product_names = [review["product_name"] for review in data]
    assert "Smartphone" in product_names
    assert "Tablet" in product_names


def test_moderate_review(client):
    client.post(
        "/customers",
        json={
            "fullname": "Tim Berners-Lee",
            "username": "tbernerslee",
            "password": "password123",
        },
    )
    response = client.post(
        "/inventory",
        json={
            "name": "Router",
            "category": "electronics",
            "price_per_item": 129.99,
            "count_in_stock": 25,
        },
    )
    item_id = response.get_json()["id"]
    response = client.post(
        "/reviews",
        json={
            "username": "tbernerslee",
            "item_id": item_id,
            "rating": 2,
            "comment": "Not satisfied with the performance.",
        },
    )
    review_id = response.get_json()["review_id"]
    response = client.patch(
        f"/reviews/{review_id}/moderate", json={"is_approved": True}
    )
    assert response.status_code == 200
    assert response.get_json()["message"] == "Review moderation updated"
    response = client.get(f"/reviews/product/{item_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["review_id"] == review_id


def test_get_review_details(client):
    client.post(
        "/customers",
        json={
            "fullname": "Steve Wozniak",
            "username": "swozniak",
            "password": "password123",
        },
    )
    response = client.post(
        "/inventory",
        json={
            "name": "Smartwatch",
            "category": "electronics",
            "price_per_item": 299.99,
            "count_in_stock": 30,
        },
    )
    item_id = response.get_json()["id"]
    response = client.post(
        "/reviews",
        json={
            "username": "swozniak",
            "item_id": item_id,
            "rating": 5,
            "comment": "Love this smartwatch!",
        },
    )
    review_id = response.get_json()["review_id"]
    response = client.get(f"/reviews/{review_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["username"] == "swozniak"
    assert data["product_name"] == "Smartwatch"
    assert data["rating"] == 5
    assert data["comment"] == "Love this smartwatch!"