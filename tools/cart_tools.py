"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
from typing import Union, Dict, List
from langchain_core.tools import tool
import sqlite3
import os
from utils.logger import logger

# 定义数据库路径
db = os.path.join(os.path.dirname(__file__), "../data/ecommerce.db")


def view_cart(user_id: int, conn=None) -> List[Dict]:
    """
    View the contents of the user's shopping cart.

    Args:
        user_id (int): The ID of the user.
        conn:
    Returns:
        List[Dict]: A list of products in the user's cart with their quantities.
    """
    if not conn:
        logger.info(f"Retrieving cart contents for user {user_id}.")
        conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        query = """
        SELECT p.id, p.name, p.price, cp.quantity
        FROM cart_products cp
        JOIN products p ON cp.product_id = p.id
        WHERE cp.cart_id = (SELECT id FROM cart WHERE user_id = ?)
        """
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        cart_items = [dict(zip([column[0] for column in cursor.description], row)) for row in results]
        logger.info(f"User {user_id}'s cart contains {len(cart_items)} items.")
        return cart_items
    except Exception as e:
        logger.error(f"Error viewing cart: {e}")
        raise
    finally:
        if not conn:
            conn.close()


def add_to_cart(user_id: int, product_id: int, quantity: int = 1, conn=None) -> str:
    """
    Add a product to the user's shopping cart.

    Args:
        user_id (int): The ID of the user.
        product_id (int): The ID of the product.
        quantity (int): Quantity to add (default is 1).
    Returns:
        str: Confirmation message.
    """
    if conn is None:
        logger.info(f"Connecting to database to retrieve cart for user {user_id}.")
        conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        # 获取用户的购物车 ID
        cursor.execute("SELECT id FROM cart WHERE user_id = ?", (user_id,))
        cart_id = cursor.fetchone()

        if not cart_id:
            # 如果用户购物车不存在，创建新的购物车
            cursor.execute("INSERT INTO cart (user_id) VALUES (?)", (user_id,))
            conn.commit()  # 提交以确保 ID 可用
            cart_id = cursor.lastrowid
        else:
            cart_id = cart_id[0]

        # 确保 cart_products 表具有唯一约束
        cursor.execute("""
            PRAGMA index_list(cart_products);
        """)
        indexes = cursor.fetchall()
        unique_constraint_found = any("cart_id" in idx[1] and "product_id" in idx[1] for idx in indexes)

        if not unique_constraint_found:
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_cart_product 
                ON cart_products(cart_id, product_id);
            """)
            conn.commit()

        # 添加或更新购物车中的产品
        cursor.execute(
            """
            INSERT INTO cart_products (cart_id, product_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(cart_id, product_id) DO UPDATE SET quantity = quantity + excluded.quantity
            """,
            (cart_id, product_id, quantity),
        )
        conn.commit()
        logger.info(f"Product {product_id} added to cart.")
        return f"Product {product_id} successfully added to your cart."
    except sqlite3.OperationalError as op_err:
        logger.error(f"Database operational error: {op_err}")
        return "Database operation failed. Please try again."
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        raise
    finally:
        if not conn:
            conn.close()



def remove_from_cart(user_id: int, product_id: int, conn=None) -> str:
    """
    Remove a product from the user's shopping cart.

    Args:
        user_id (int): The ID of the user.
        product_id (int): The ID of the product.
        conn
    Returns:
        str: Confirmation message.
    """
    if not conn:
        logger.info(f"Retrieving cart contents for user {user_id}.")
        conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        # 获取用户的购物车 ID
        cursor.execute("SELECT id FROM cart WHERE user_id = ?", (user_id,))
        cart_id = cursor.fetchone()

        if not cart_id:
            logger.warning(f"User {user_id} does not have a cart.")
            return f"No cart found for user {user_id}."

        # 删除购物车中的产品
        cursor.execute("DELETE FROM cart_products WHERE cart_id = ? AND product_id = ?", (cart_id[0], product_id))
        conn.commit()

        if cursor.rowcount > 0:
            logger.info(f"Product {product_id} removed from cart.")
            return f"Product {product_id} successfully removed from your cart."
        else:
            logger.warning(f"Product {product_id} not found in cart.")
            return f"Product {product_id} is not in your cart."
    except Exception as e:
        logger.error(f"Error removing from cart: {e}")
        raise
    finally:
        if not conn:
            conn.close()


@tool
def view_cart_tool(user_id: int) -> List[Dict]:
    """
    Retrieve the contents of a user's shopping cart.

    Args:
        user_id (int): The ID of the user.

    Returns:
        List[Dict]: A list of products in the user's cart with their details.
    """
    return view_cart(user_id)


@tool
def add_to_cart_tool(user_id: int, product_id: int, quantity: int = 1) -> str:
    """
    Add a product to a user's shopping cart.

    Args:
        user_id (int): The ID of the user.
        product_id (int): The ID of the product to add.
        quantity (int): The quantity of the product to add. Default is 1.

    Returns:
        str: A confirmation message indicating success or failure.
    """
    return add_to_cart(user_id, product_id, quantity)


@tool
def remove_from_cart_tool(user_id: int, product_id: int) -> str:
    """
    Remove a product from a user's shopping cart.

    Args:
        user_id (int): The ID of the user.
        product_id (int): The ID of the product to remove.

    Returns:
        str: A confirmation message indicating success or failure.
    """
    return remove_from_cart(user_id, product_id)


if __name__ == "__main__":
    # 测试代码
    # user_id: 1
    # product_id: 160
    # quantity: 1
    try:
        print(view_cart(user_id=1))
        print(add_to_cart(user_id=1, product_id=101, quantity=2))
        print(remove_from_cart(user_id=1, product_id=101))
    except Exception as e:
        print(f"Test failed: {e}")
