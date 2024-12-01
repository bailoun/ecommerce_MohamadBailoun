import boto3
import json
import psycopg2
from flask import g
from botocore.exceptions import ClientError

_cached_secret = None


def get_secret():
    """
    Fetches the database credentials from AWS Secrets Manager. Caches the result
    to prevent multiple requests for the same secret.

    Returns:
        dict: A dictionary containing the secret values, including DB_USER and DB_PASSWORD.
    """
    global _cached_secret

    if _cached_secret:
        return _cached_secret

    secret_name = "ecommerce_db/db_credentials"
    region_name = "eu-north-1"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    secret = get_secret_value_response["SecretString"]
    secret_dict = json.loads(secret)

    _cached_secret = secret_dict

    return secret_dict


def get_db_credentials():
    """
    Retrieves the database credentials (username and password) from the aws secret manager.

    Returns:
        tuple: A tuple containing the database username and password.
    """
    secret = get_secret()
    db_user = secret.get("DB_USER")
    db_password = secret.get("DB_PASSWORD")

    return db_user, db_password


DB_NAME = "ecommerce_db"
DB_HOST = "postgres"
DB_PORT = "5432"


def get_db():
    """
    Returns a database connection object, creating a new connection if none exists.

    Uses Flask's `g` object to store the connection, which is accessible throughout the request lifecycle.

    Returns:
        connection: A psycopg2 database connection object.
    """
    if "db" not in g:
        db_user, db_password = get_db_credentials()

        g.db = psycopg2.connect(
            database=DB_NAME,
            user=db_user,
            password=db_password,
            host=DB_HOST,
            port=DB_PORT,
        )
    return g.db


def close_db(e=None):
    """
    Closes the current database connection stored in Flask's `g` object.

    Args:
        e (optional): An exception that may have been raised during request handling.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db_connection():
    """
    Initializes a new database connection (used during the setup process) and immediately closes it.

    This function is typically called at the application startup.
    """
    db_user, db_password = get_db_credentials()

    conn = psycopg2.connect(
        database=DB_NAME,
        user=db_user,
        password=db_password,
        host=DB_HOST,
        port=DB_PORT,
    )
    conn.close()
