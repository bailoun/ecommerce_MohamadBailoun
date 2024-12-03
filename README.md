### **Project Title: EECE435L Final Project**

#### **Description**
This project is an eCommerce system built with Flask, featuring functionalities such as customer management, inventory management, sales processing, and product reviews. It includes database integration, rate-limiting, and AWS Secrets Manager for secure credential management.

---

#### **Features**
1. **Customers Service**: Manage customer accounts and wallets.
2. **Inventory Service**: Add, update, and manage inventory items.
3. **Sales Service**: Process purchases and track historical sales.
4. **Reviews Service**: Submit, update, and moderate product reviews.
5. **Rate-Limiting**: Prevent abuse by limiting API requests.
6. **AWS Secrets Manager Integration**: Securely fetch database credentials.

---

#### **Setup and Installation**
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/bailoun/ecommerce_MohamadBailoun
   cd ecommerce_MohamadBailoun
   ```

2. **Run the Application with Docker**:
   - Ensure Docker is installed and running.
   - Start all services using:
     ```bash
     docker-compose up
     ```

3. **Access the Application**:
   - The services run on:
     - Customers Service: `http://127.0.0.1:5001`
     - Inventory Service: `http://127.0.0.1:5002`
     - Sales Service: `http://127.0.0.1:5003`
     - Reviews Service: `http://127.0.0.1:5004`
   - PostgreSQL runs on `http://127.0.0.1:5432`.

---

#### **Testing**
Run tests using `pytest`:
```bash
pytest
```

---

#### **Key Files**
- `docker-compose.yml`: Orchestrates all services and the database.
- `Dockerfile`: Defines dependencies and runtime for each service.
- `app.py`: Main entry point for the Flask application.
- `requirements.txt`: Lists Python dependencies.
- `conftest.py`: Test setup for pytest.

---

#### **Acknowledgments**
This project is part of the EECE435L course and showcases various system design and implementation techniques, including Docker containerization and AWS integration.
