import sqlite3
from datetime import datetime, timedelta

DB_PATH = "manufacturing.db"


def create_schema(conn):
    """Create the manufacturing database schema with 5 tables."""
    cursor = conn.cursor()

    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit_price REAL NOT NULL,
            lead_time_days INTEGER NOT NULL
        )
    """)

    # Create parts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            quantity_per_unit INTEGER NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # Create inventory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY,
            part_id INTEGER NOT NULL,
            warehouse_location TEXT NOT NULL,
            quantity_on_hand INTEGER NOT NULL,
            reorder_level INTEGER NOT NULL,
            FOREIGN KEY (part_id) REFERENCES parts(id)
        )
    """)

    # Create production_orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_orders (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    conn.commit()


def seed_data(conn):
    """Insert sample manufacturing data into the database."""
    cursor = conn.cursor()

    # Insert products
    products = [
        ("Widget A", "Widgets", 49.99, 5),
        ("Widget B", "Widgets", 59.99, 7),
        ("Gadget X", "Gadgets", 99.99, 10),
        ("Gadget Y", "Gadgets", 129.99, 14),
        ("Component Z", "Components", 19.99, 3),
    ]
    cursor.executemany(
        "INSERT INTO products (name, category, unit_price, lead_time_days) VALUES (?, ?, ?, ?)",
        products,
    )

    # Insert parts
    parts = [
        ("Spring", 1, 4),
        ("Bolt", 1, 8),
        ("Washer", 1, 12),
        ("Resistor", 2, 6),
        ("Capacitor", 2, 4),
        ("Diode", 3, 2),
        ("Connector", 3, 3),
        ("Screw", 4, 10),
    ]
    cursor.executemany(
        "INSERT INTO parts (name, product_id, quantity_per_unit) VALUES (?, ?, ?)", parts
    )

    # Insert inventory records
    inventory = [
        (1, "Warehouse A", 500, 100),
        (2, "Warehouse B", 300, 80),
        (3, "Warehouse C", 200, 50),
        (4, "Warehouse A", 150, 40),
        (5, "Warehouse B", 600, 150),
        (6, "Warehouse C", 400, 100),
        (7, "Warehouse A", 250, 60),
        (8, "Warehouse B", 1000, 200),
    ]
    cursor.executemany(
        "INSERT INTO inventory (part_id, warehouse_location, quantity_on_hand, reorder_level) VALUES (?, ?, ?, ?)",
        inventory,
    )

    # Insert production orders with varying statuses
    today = datetime.now()
    production_orders = [
        (1, today.isoformat(), (today + timedelta(days=5)).isoformat(), "pending", 100),
        (2, (today - timedelta(days=2)).isoformat(), (today + timedelta(days=3)).isoformat(), "in_progress", 50),
        (3, (today - timedelta(days=5)).isoformat(), (today - timedelta(days=1)).isoformat(), "completed", 25),
        (4, (today - timedelta(days=1)).isoformat(), (today + timedelta(days=7)).isoformat(), "pending", 75),
        (5, (today - timedelta(days=3)).isoformat(), (today + timedelta(days=2)).isoformat(), "in_progress", 40),
    ]
    cursor.executemany(
        "INSERT INTO production_orders (product_id, order_date, due_date, status, quantity) VALUES (?, ?, ?, ?, ?)",
        production_orders,
    )

    # Insert demo users
    users = [
        ("operator1", "operator"),
        ("operator2", "operator"),
        ("supervisor1", "supervisor"),
        ("supervisor2", "supervisor"),
        ("director1", "director"),
    ]
    cursor.executemany(
        "INSERT INTO users (username, role) VALUES (?, ?)", users
    )

    conn.commit()


def main():
    """Initialize the manufacturing database with schema and sample data."""
    try:
        conn = sqlite3.connect(DB_PATH)
        create_schema(conn)
        seed_data(conn)
        conn.close()
        print(f"✓ Database created at {DB_PATH}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
