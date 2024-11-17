"""
@Time ： 2024-11-16
@Auth ： Adam Lyu
"""
import sqlite3
from pprint import pprint
from scripts.initialize_db import create_test_database_and_tables
from tools.cart_tools import (
    view_cart,
    add_to_cart,
    remove_from_cart,
)

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
    INSERT INTO orders (user_id, total_amount, status, delivery_address)
    VALUES (1, 50.0, 'Pending', '123 Test Address')
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


def test_view_cart(conn):
    print("Testing view_cart...")
    pprint(view_cart(1, conn=conn))


def test_add_to_cart(conn):
    print("Testing add_to_cart...")
    print(add_to_cart(1, 3, 2, conn=conn))  # Add Product C
    pprint(view_cart(1, conn=conn))


def test_remove_from_cart(conn):
    print("Testing remove_from_cart...")
    print(remove_from_cart(1, 1, conn=conn))  # Remove Product A
    pprint(view_cart(1, conn=conn))


def test_checkout_order(conn):
    print("Testing checkout_order...")
    print(checkout_order(1, conn=conn))


def test_search_orders(conn):
    print("Testing search_orders...")
    pprint(search_orders(1, conn=conn))


def test_update_delivery_address(conn):
    print("Testing update_delivery_address...")
    print(update_delivery_address(1, "456 New Address", conn=conn))


def test_cancel_order(conn):
    print("Testing cancel_order...")
    print(cancel_order(1, "User decided not to proceed.", conn=conn))


def test_get_recent_orders(conn):
    print("Testing get_recent_orders...")
    pprint(get_recent_orders(1, 30, conn=conn))


def test_list_categories(conn):
    print("Testing list_categories...")
    pprint(list_categories(conn=conn))


def test_search_and_recommend_products(conn):
    print("Testing search_and_recommend_products...")
    pprint(search_and_recommend_products(name="Product", category="Category 1", price_range="10-30", conn=conn))


def main():
    # 创建测试数据库
    conn = create_test_database_and_tables()

    # 填充测试数据
    populate_test_data(conn)

    # 运行测试
    test_view_cart(conn)
    test_add_to_cart(conn)
    test_remove_from_cart(conn)
    test_checkout_order(conn)
    test_search_orders(conn)
    test_update_delivery_address(conn)
    test_cancel_order(conn)
    test_get_recent_orders(conn)
    test_list_categories(conn)
    test_search_and_recommend_products(conn)

    # 关闭连接
    conn.close()


if __name__ == "__main__":
    main()
