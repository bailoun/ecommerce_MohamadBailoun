def test_register_customer(client):
    response = client.post(
        "/customers",
        json={
            "fullname": "John Doe",
            "username": "johndoe",
            "password": "password123",
            "age": 30,
            "address": "123 Main St",
            "gender": "M",
            "marital_status": False,
        },
    )
    assert response.status_code == 201
    assert response.get_json() == {"message": "Customer registered successfully"}

    response = client.post(
        "/customers",
        json={
            "username": "janedoe",
            "password": "password123",
        },
    )
    assert response.status_code == 400
    assert (
        "fullname, username, and password are required" in response.get_json()["error"]
    )

    response = client.post(
        "/customers",
        json={
            "fullname": "John Smith",
            "username": "johndoe",
            "password": "password123",
        },
    )
    assert response.status_code == 409
    assert response.get_json() == {"error": "Username is already taken"}


def test_get_customer_by_username(client):
    client.post(
        "/customers",
        json={
            "fullname": "Alice Smith",
            "username": "alicesmith",
            "password": "password123",
        },
    )

    response = client.get("/customers/alicesmith")
    assert response.status_code == 200
    data = response.get_json()
    assert data["username"] == "alicesmith"
    assert data["fullname"] == "Alice Smith"

    response = client.get("/customers/nonexistent")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Customer not found"}


def test_delete_customer(client):
    client.post(
        "/customers",
        json={
            "fullname": "Bob Johnson",
            "username": "bobjohnson",
            "password": "password123",
        },
    )

    response = client.delete("/customers/bobjohnson")
    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Customer 'bobjohnson' deleted successfully"
    }

    response = client.get("/customers/bobjohnson")
    assert response.status_code == 404


def test_update_customer(client):
    client.post(
        "/customers",
        json={
            "fullname": "Charlie Brown",
            "username": "charliebrown",
            "password": "password123",
        },
    )

    response = client.put(
        "/customers/charliebrown",
        json={
            "age": 28,
            "address": "456 Elm St",
        },
    )
    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Customer 'charliebrown' updated successfully"
    }

    response = client.get("/customers/charliebrown")
    assert response.status_code == 200
    data = response.get_json()
    assert data["age"] == 28
    assert data["address"] == "456 Elm St"


def test_charge_customer_wallet(client):
    client.post(
        "/customers",
        json={
            "fullname": "Diana Prince",
            "username": "wonderwoman",
            "password": "password123",
            "wallet_balance": 100,
        },
    )

    response = client.post("/customers/wonderwoman/charge", json={"amount": 50})
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Wallet charged successfully"
    assert int(data["new_balance"]) == 150


def test_deduct_money_from_wallet(client):
    client.post(
        "/customers",
        json={
            "fullname": "Bruce Wayne",
            "username": "batman",
            "password": "password123",
            "wallet_balance": 200,
        },
    )

    response = client.post("/customers/batman/deduct", json={"amount": 50})
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Amount deducted successfully"
    assert int(data["new_balance"]) == 150

    response = client.post("/customers/batman/deduct", json={"amount": 300})
    assert response.status_code == 400
    assert response.get_json() == {"error": "Insufficient funds"}

    response = client.post("/customers/batman/deduct", json={"amount": -10})
    assert response.status_code == 400
    assert "Invalid amount" in response.get_json()["error"]


def test_get_all_customers(client):
    client.post(
        "/customers",
        json={
            "fullname": "Clark Kent",
            "username": "superman",
            "password": "password123",
        },
    )
    client.post(
        "/customers",
        json={
            "fullname": "Hal Jordan",
            "username": "greenlantern",
            "password": "password123",
        },
    )

    response = client.get("/customers")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    usernames = [customer["username"] for customer in data]
    assert "superman" in usernames
    assert "greenlantern" in usernames
