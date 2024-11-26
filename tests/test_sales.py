def test_display_available_goods(client):
    client.post(
        "/inventory",
        json={
            "name": "Laptop",
            "category": "electronics",
            "price_per_item": 1200.00,
            "count_in_stock": 5,
        },
    )
    client.post(
        "/inventory",
        json={
            "name": "Jeans",
            "category": "clothes",
            "price_per_item": 50.00,
            "count_in_stock": 0,
        },
    )
    response = client.get("/sales/goods")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop"
    assert float(data[0]["price_per_item"]) == 1200.00


def test_get_good_details(client):
    response = client.post(
        "/inventory",
        json={
            "name": "Smartphone",
            "category": "electronics",
            "price_per_item": 800.00,
            "description": "Latest model",
            "count_in_stock": 10,
        },
    )
    item_id = response.get_json()["id"]
    response = client.get(f"/sales/goods/{item_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Smartphone"
    assert data["description"] == "Latest model"
    assert data["count_in_stock"] == 10
    response = client.get("/sales/goods/9999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Item not found"}


def test_make_purchase(client):
    client.post(
        "/customers",
        json={
            "fullname": "Eve Adams",
            "username": "eveadams",
            "password": "password123",
            "wallet_balance": 5000.00,
        },
    )

    response = client.post(
        "/inventory",
        json={
            "name": "Electric Guitar",
            "category": "accessories",
            "price_per_item": 700.00,
            "count_in_stock": 2,
        },
    )
    item_id = response.get_json()["id"]

    response = client.post(
        "/sales/purchase",
        json={"username": "eveadams", "item_id": item_id, "quantity": 1},
    )
    assert response.status_code == 200
    assert response.get_json() == {"message": "Purchase successful"}

    response = client.get("/customers/eveadams")
    assert response.status_code == 200
    customer = response.get_json()
    assert float(customer["wallet_balance"]) == 4300.00

    response = client.get(f"/sales/goods/{item_id}")
    assert response.status_code == 200
    item = response.get_json()
    assert item["count_in_stock"] == 1

    response = client.post(
        "/sales/purchase",
        json={"username": "eveadams", "item_id": item_id, "quantity": 5},
    )
    assert response.status_code == 400
    assert "Not enough stock available" in response.get_json()["error"]

    client.post("/customers/eveadams/deduct", json={"amount": 4000})
    response = client.post(
        "/sales/purchase",
        json={"username": "eveadams", "item_id": item_id, "quantity": 1},
    )
    assert response.status_code == 400
    assert "Insufficient funds" in response.get_json()["error"]

    response = client.post(
        "/sales/purchase",
        json={"username": "eveadams", "item_id": item_id, "quantity": -1},
    )
    assert response.status_code == 400
    assert "Quantity must be positive" in response.get_json()["error"]


def test_get_customer_purchases(client):
    client.post(
        "/customers",
        json={
            "fullname": "Frank Miller",
            "username": "frankmiller",
            "password": "password123",
            "wallet_balance": 1000.00,
        },
    )

    response = client.post(
        "/inventory",
        json={
            "name": "Book A",
            "category": "accessories",
            "price_per_item": 30.00,
            "count_in_stock": 5,
        },
    )
    item_id_a = response.get_json()["id"]
    response = client.post(
        "/inventory",
        json={
            "name": "Book B",
            "category": "accessories",
            "price_per_item": 25.00,
            "count_in_stock": 5,
        },
    )
    item_id_b = response.get_json()["id"]

    client.post(
        "/sales/purchase",
        json={"username": "frankmiller", "item_id": item_id_a, "quantity": 2},
    )
    client.post(
        "/sales/purchase",
        json={"username": "frankmiller", "item_id": item_id_b, "quantity": 1},
    )

    response = client.get("/sales/customers/frankmiller/purchases")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2

    purchase1 = data[0]
    purchase2 = data[1]
    assert purchase1["quantity"] in [1, 2]
    assert purchase1["item"]["name"] in ["Book A", "Book B"]
    assert purchase2["item"]["name"] in ["Book A", "Book B"]

    response = client.get("/sales/customers/nonexistentuser/purchases")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Customer not found"}
