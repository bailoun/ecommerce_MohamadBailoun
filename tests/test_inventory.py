from memory_profiler import profile


@profile
def test_add_goods(client):
    response = client.post(
        "/inventory",
        json={
            "name": "Apple iPhone",
            "category": "electronics",
            "price_per_item": 999.99,
            "description": "Latest model",
            "count_in_stock": 10,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Item added successfully"
    assert "id" in data

    response = client.post(
        "/inventory",
        json={
            "category": "electronics",
            "price_per_item": 999.99,
            "count_in_stock": 10,
        },
    )
    assert response.status_code == 400
    assert "Missing required fields" in response.get_json()["error"]

    response = client.post(
        "/inventory",
        json={
            "name": "Orange",
            "category": "fruits",
            "price_per_item": 1.99,
            "count_in_stock": 100,
        },
    )
    assert response.status_code == 400
    assert "Invalid category" in response.get_json()["error"]

    response = client.post(
        "/inventory",
        json={
            "name": "Faulty Item",
            "category": "electronics",
            "price_per_item": -50,
            "count_in_stock": 5,
        },
    )
    assert response.status_code == 400
    assert (
        "Price and count_in_stock must be non-negative" in response.get_json()["error"]
    )


@profile
def test_deduct_goods(client):
    response = client.post(
        "/inventory",
        json={
            "name": "Samsung TV",
            "category": "electronics",
            "price_per_item": 499.99,
            "count_in_stock": 5,
        },
    )
    item_id = response.get_json()["id"]

    response = client.patch(f"/inventory/{item_id}/deduct", json={"quantity": 2})
    assert response.status_code == 200
    assert response.get_json() == {"message": "Stock deducted successfully"}

    response = client.patch(f"/inventory/{item_id}/deduct", json={"quantity": 10})
    assert response.status_code == 400
    assert "Not enough stock available" in response.get_json()["error"]

    response = client.patch(f"/inventory/{item_id}/deduct", json={"quantity": -1})
    assert response.status_code == 400
    assert "Invalid quantity" in response.get_json()["error"]


@profile
def test_update_goods(client):
    response = client.post(
        "/inventory",
        json={
            "name": "Nike Shoes",
            "category": "clothes",
            "price_per_item": 79.99,
            "count_in_stock": 50,
        },
    )
    item_id = response.get_json()["id"]

    response = client.put(
        f"/inventory/{item_id}", json={"price_per_item": 69.99, "count_in_stock": 45}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Item updated successfully"
    assert data["id"] == item_id

    response = client.put(f"/inventory/{item_id}", json={"category": "vehicles"})
    assert response.status_code == 400
    assert "Invalid category" in response.get_json()["error"]

    response = client.put(f"/inventory/9999", json={"price_per_item": 59.99})
    assert response.status_code == 404
    assert "Item not found" in response.get_json()["error"]
