import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",  # change if needed
    password="your_mysql_password"  # change to your password
)
cursor = conn.cursor()

# Create database and tables
cursor.execute("CREATE DATABASE IF NOT EXISTS inventory_system")
cursor.execute("USE inventory_system")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category_id INT,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES Category(category_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Stock (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    quantity INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
)
""")

# ---------- FUNCTIONS ----------

def add_category():
    name = input("Enter category name: ")
    cursor.execute("INSERT IGNORE INTO Category (name) VALUES (%s)", (name,))
    conn.commit()
    print("✅ Category added.")

def add_product():
    view_categories()
    name = input("Enter product name: ")
    category_id = int(input("Enter category ID: "))
    price = float(input("Enter price: "))
    quantity = int(input("Enter initial stock quantity: "))

    cursor.execute("INSERT INTO Product (name, category_id, price) VALUES (%s, %s, %s)", (name, category_id, price))
    product_id = cursor.lastrowid
    cursor.execute("INSERT INTO Stock (product_id, quantity) VALUES (%s, %s)", (product_id, quantity))
    conn.commit()
    print("✅ Product added.")

def view_categories():
    cursor.execute("SELECT * FROM Category")
    rows = cursor.fetchall()
    print("\n📁 Categories:")
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}")

def view_inventory():
    cursor.execute("""
        SELECT p.product_id, p.name, c.name AS category, p.price, s.quantity
        FROM Product p
        JOIN Category c ON p.category_id = c.category_id
        JOIN Stock s ON p.product_id = s.product_id
    """)
    results = cursor.fetchall()
    print("\n📦 Inventory:")
    for row in results:
        print(f"ID:{row[0]}, Name:{row[1]}, Category:{row[2]}, Price:{row[3]}, Stock:{row[4]}")

def update_stock():
    view_inventory()
    product_id = int(input("Enter product ID to update stock: "))
    quantity = int(input("Enter new quantity: "))
    cursor.execute("UPDATE Stock SET quantity = %s WHERE product_id = %s", (quantity, product_id))
    conn.commit()
    print("✅ Stock updated.")

def delete_product():
    view_inventory()
    product_id = int(input("Enter product ID to delete: "))
    cursor.execute("DELETE FROM Stock WHERE product_id = %s", (product_id,))
    cursor.execute("DELETE FROM Product WHERE product_id = %s", (product_id,))
    conn.commit()
    print("🗑️ Product deleted.")

def low_stock_report():
    threshold = int(input("Enter stock threshold: "))
    cursor.execute("""
        SELECT p.name, s.quantity
        FROM Product p
        JOIN Stock s ON p.product_id = s.product_id
        WHERE s.quantity < %s
    """, (threshold,))
    results = cursor.fetchall()
    print("\n⚠️ Low Stock Items:")
    for row in results:
        print(f"{row[0]} → Quantity: {row[1]}")

def total_stock_value():
    cursor.execute("""
        SELECT SUM(p.price * s.quantity) AS total_value
        FROM Product p
        JOIN Stock s ON p.product_id = s.product_id
    """)
    value = cursor.fetchone()[0]
    print("\n💰 Total Inventory Value:", value if value else 0)

# ---------- MENU ----------

def main():
    while True:
        print("\n📋 INVENTORY MANAGEMENT MENU")
        print("1. Add Category")
        print("2. Add Product")
        print("3. View Categories")
        print("4. View Inventory")
        print("5. Update Stock")
        print("6. Delete Product")
        print("7. Low Stock Report")
        print("8. Total Inventory Value")
        print("9. Exit")

        choice = input("Enter your choice (1-9): ")

        if choice == '1':
            add_category()
        elif choice == '2':
            add_product()
        elif choice == '3':
            view_categories()
        elif choice == '4':
            view_inventory()
        elif choice == '5':
            update_stock()
        elif choice == '6':
            delete_product()
        elif choice == '7':
            low_stock_report()
        elif choice == '8':
            total_stock_value()
        elif choice == '9':
            print("👋 Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

# Run the program
main()

# Close connection
cursor.close()
conn.close()
