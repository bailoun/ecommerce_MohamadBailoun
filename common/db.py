import boto3
import json
import psycopg2
from flask import g
from botocore.exceptions import ClientError

_cached_secret = None


def get_secret():
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
    secret = get_secret()
    db_user = secret.get("DB_USER")
    db_password = secret.get("DB_PASSWORD")

    return db_user, db_password


DB_NAME = "ecommerce_db"
DB_HOST = "localhost"
DB_PORT = "5432"


def get_db():
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
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db_connection():
    db_user, db_password = get_db_credentials()

    conn = psycopg2.connect(
        database=DB_NAME,
        user=db_user,
        password=db_password,
        host=DB_HOST,
        port=DB_PORT,
    )
    conn.close()
