"""
@Time ： 2024-11-16
@Auth ： Adam Lyu
"""
import unittest
import sqlite3
from pprint import pprint
from scripts.initialize_db import create_tables
from tools.cart_tools import view_cart, add_to_cart, remove_from_cart
from tools.order_tools import (
    checkout_order,
    search_orders,
    update_delivery_address,
    cancel_order,
    get_recent_orders
)
from tools.product_tools import list_categories, search_and_recommend_products


def populate_test_data(conn):
    """
    Populate the test database with initial data for testing.
    Args:
        conn: SQLite connection object.
    """
    cursor = conn.cursor()

    # 添加产品
    cursor.executemany("""
    INSERT INTO products (name, description, price, stock, category)
    VALUES (?, ?, ?, ?, ?)
    """, [
        ("Product A", "Description A", 10.0, 100, "Category 1"),
        ("Product B", "Description B", 20.0, 50, "Category 1"),
        ("Product C", "Description C", 15.0, 30, "Category 2"),
        ("Product D", "Description D", 25.0, 10, "Category 3"),
    ])

    # 添加用户购物车
    cursor.execute("INSERT INTO cart (user_id) VALUES (1)")
    cart_id = cursor.lastrowid

    # 添加购物车产品
    cursor.executemany("""
    INSERT INTO cart_products (cart_id, product_id, quantity)
    VALUES (?, ?, ?)
    """, [
        (cart_id, 1, 2),  # Product A
        (cart_id, 2, 1),  # Product B
    ])

    # 添加订单
    cursor.execute("""
    INSERT INTO orders (user_id, total_amount, status, delivery_address, payment_method)
    VALUES (1, 50.0, 'Pending', '123 Test Address', 'Credit Card')
    """)
    order_id = cursor.lastrowid

    # 添加订单产品
    cursor.executemany("""
    INSERT INTO order_products (order_id, product_id, quantity, price)
    VALUES (?, ?, ?, ?)
    """, [
        (order_id, 1, 2, 10.0),
        (order_id, 2, 1, 20.0),
    ])

    conn.commit()


def create_test_database_and_tables():
    """
    创建 SQLite 内存数据库及相关表，用于测试环境。
    Returns:
        conn: sqlite3.Connection 对象
    """
    try:
        connection = sqlite3.connect(":memory:")
        cursor = connection.cursor()
        create_tables(cursor)
        connection.commit()
        print("In-memory test database and tables created successfully!")
        return connection

    except sqlite3.Error as e:
        print(f"An error occurred while creating the in-memory test database: {e}")
        raise


class TestEcommerceSystem(unittest.TestCase):
    def setUp(self):
        """Set up a new test database connection for each test."""
        self.conn = create_test_database_and_tables()
        populate_test_data(self.conn)

    def tearDown(self):
        """Close the test database connection after each test."""
        self.conn.close()

    def test_view_cart(self):
        """Test viewing the cart."""
        result = view_cart(1, conn=self.conn)
        pprint(result)
        self.assertTrue(len(result) > 0, "Cart should not be empty.")

    def test_add_to_cart(self):
        """Test adding an item to the cart."""
        result = add_to_cart(1, 3, 2, conn=self.conn)  # Add Product C
        self.assertEqual(result, "Product 3 successfully added to your cart.", "Product should be added successfully.")
        cart = view_cart(1, conn=self.conn)
        # Update field to match 'id' instead of 'product_id'
        self.assertTrue(any(item["id"] == 3 for item in cart), "Product C should be in the cart.")

    def test_remove_from_cart(self):
        """Test removing an item from the cart."""
        result = remove_from_cart(1, 1, conn=self.conn)  # Remove Product A
        self.assertEqual(result, "Product removed from cart.", "Product should be removed successfully.")
        cart = view_cart(1, conn=self.conn)
        self.assertFalse(any(item["product_id"] == 1 for item in cart), "Product A should not be in the cart.")

    def test_checkout_order(self):
        """Test checkout process."""
        result = checkout_order(1, "789 Test Street", "PayPal", conn=self.conn)
        print(result)
        self.assertIn("Checkout successful", result, "Checkout should be successful.")

    def test_search_orders(self):
        """Test searching orders."""
        result = search_orders(1, conn=self.conn)
        pprint(result)
        self.assertTrue(len(result) > 0, "There should be at least one order.")

    def test_update_delivery_address(self):
        """Test updating the delivery address."""
        result = update_delivery_address(1, "456 New Address", conn=self.conn)
        self.assertEqual(result, "Delivery address updated successfully.", "Address should be updated.")

    def test_cancel_order(self):
        """Test cancelling an order."""
        result = cancel_order(1, "Changed my mind.", conn=self.conn)
        self.assertEqual(result, "Order cancelled successfully.", "Order should be cancelled.")

    def test_get_recent_orders(self):
        """Test retrieving recent orders."""
        result = get_recent_orders(1, 30, conn=self.conn)
        pprint(result)
        self.assertTrue(len(result) > 0, "There should be recent orders.")

    def test_list_categories(self):
        """Test listing product categories."""
        result = list_categories(conn=self.conn)
        pprint(result)
        self.assertTrue(len(result) > 0, "There should be categories listed.")

    def test_search_and_recommend_products(self):
        """Test searching and recommending products."""
        result = search_and_recommend_products(name="Product", category="Category 1", price_range="10-30", conn=self.conn)
        pprint(result)
        self.assertTrue(len(result) > 0, "There should be at least one recommended product.")


if __name__ == "__main__":
    unittest.main()
