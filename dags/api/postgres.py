import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

host = os.getenv('DB_HOST')
database = os.getenv('DB_DATABASE')
port = os.getenv('DB_PORT')
user = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')

def postgres_connection():
    return psycopg2.connect(
        dbname=database,
        user=user,
        password=password,
        host=host,  
        port=port
    )

def create_table(conn):
    """Create table if it does not exist."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders_created (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    order_type VARCHAR(255) NOT NULL,
                    price_taken DECIMAL NOT NULL,
                    order_amount DECIMAL NOT NULL,
                    algo_strategy VARCHAR(255) NOT NULL,
                    order_executed BOOLEAN
                );
            """)
            conn.commit()
            print("Table created successfully or already exists.")
            return "Table created successfully or already exists."
    except Exception as e:
        print("Failed to create table:", e)
        conn.rollback()
        return 'Table creation failed'

def qry_create_order(message):
    query = """INSERT INTO orders_created (timestamp, order_type, price_taken, order_amount, algo_strategy, order_executed)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON CONFLICT (id) DO UPDATE SET
               timestamp = EXCLUDED.timestamp,
               order_type = EXCLUDED.order_type,
               price_taken = EXCLUDED.price_taken,
               order_amount = EXCLUDED.order_amount,
               algo_strategy = EXCLUDED.algo_strategy,
               order_executed = EXCLUDED.order_executed;
            """
    params = tuple(message)
    return query, params

def insert_order(message):
    try:
        with postgres_connection() as conn:
            response = create_table(conn)
            if response == 'Table creation failed':
                return response

            query, params = qry_create_order(message)
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                print("Order inserted successfully.")
                return "Order inserted successfully."
    except Exception as e:
        print("Error inserting order:", e)
        if conn:
            conn.rollback()

def get_orders_today(order_type, algo_strategy):
    try:
        with postgres_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                hoy = datetime.now().date()
                query = """
                    SELECT * FROM orders_created
                    WHERE DATE(timestamp) = %s AND order_executed = TRUE AND order_type = %s AND algo_strategy = %s;
                """
                cursor.execute(query, (hoy, order_type, algo_strategy))
                results = cursor.fetchall()
                return results
    except Exception as e:
        print("Error retrieving orders:", e)
        return []