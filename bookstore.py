import sqlite3
import os
from datetime import datetime

DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "bookstore.db")
os.makedirs(DB_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    price REAL,
    stock INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    order_date TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    book_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
)
""")

conn.commit()

def add_book():
    title = input("Title: ")
    author = input("Author: ")
    price = float(input("Price: "))
    stock = int(input("Stock: "))

    cursor.execute("""
    INSERT INTO books (title, author, price, stock)
    VALUES (?, ?, ?, ?)
    """, (title, author, price, stock))
    conn.commit()
    print("✅ Book added")

def add_customer():
    name = input("Customer name: ")
    email = input("Email: ")

    cursor.execute("""
    INSERT OR IGNORE INTO customers (name, email)
    VALUES (?, ?)
    """, (name, email))
    conn.commit()
    print("✅ Customer added")

def place_order():
    customer_id = int(input("Customer ID: "))
    cursor.execute("INSERT INTO orders (customer_id, order_date) VALUES (?, ?)",
                   (customer_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    order_id = cursor.lastrowid

    while True:
        book_id = int(input("Book ID (0 to finish): "))
        if book_id == 0:
            break
        qty = int(input("Quantity: "))

        cursor.execute("""
        INSERT INTO order_items (order_id, book_id, quantity)
        VALUES (?, ?, ?)
        """, (order_id, book_id, qty))

        cursor.execute("UPDATE books SET stock = stock - ? WHERE id = ?", (qty, book_id))

    conn.commit()
    print("🛒 Order placed successfully")

def view_orders():
    cursor.execute("""
    SELECT o.id, c.name, o.order_date, SUM(b.price * oi.quantity)
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    JOIN order_items oi ON o.id = oi.order_id
    JOIN books b ON oi.book_id = b.id
    GROUP BY o.id
    """)
    rows = cursor.fetchall()

    print("\nOrderID | Customer | Date | Total Amount")
    print("-" * 60)
    for row in rows:
        print(row)

def menu():
    while True:
        print("""
====== Online Bookstore ======
1. Add Book
2. Add Customer
3. Place Order
4. View Orders
5. Exit
""")
        choice = input("Enter choice: ")

        if choice == "1":
            add_book()
        elif choice == "2":
            add_customer()
        elif choice == "3":
            place_order()
        elif choice == "4":
            view_orders()
        elif choice == "5":
            print("👋 Exiting system")
            break
        else:
            print("❌ Invalid choice")

menu()
conn.close()
