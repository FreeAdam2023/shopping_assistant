"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
from langchain_core.tools import tool
import sqlite3
import os
from utils.logger import logger

# 定义数据库路径
db = os.path.join(os.path.dirname(__file__), "../data/database.db")


@tool
def checkout(user_id: int) -> str:
    """
    Proceed to checkout for the user's cart.

    Args:
        user_id (int): The ID of the user.

    Returns:
        str: Confirmation of the checkout process.
    """
    logger.info(f"Processing checkout for user {user_id}.")
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        # Retrieve cart contents
        cursor.execute("SELECT product_id, quantity FROM cart WHERE user_id = ?", (user_id,))
        cart_contents = cursor.fetchall()

        if not cart_contents:
            logger.warning("Cart is empty.")
            return "Your cart is empty. Please add items before checking out."

        # Create an order
        cursor.execute("INSERT INTO orders (user_id, created_at) VALUES (?, datetime('now'))", (user_id,))
        order_id = cursor.lastrowid

        # Insert order details
        for product_id, quantity in cart_contents:
            cursor.execute(
                "INSERT INTO order_details (order_id, product_id, quantity) VALUES (?, ?, ?)",
                (order_id, product_id, quantity),
            )

        # Clear the cart
        cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        conn.commit()

        logger.info(f"Checkout complete for user {user_id}. Order ID: {order_id}.")
        return f"Checkout successful! Your order ID is {order_id}."
    except Exception as e:
        logger.error(f"Error during checkout for user {user_id}: {e}")
        raise
    finally:
        conn.close()


@tool
def search_orders(order_id: int) -> str:
    """
    Get the status of a specific order.

    Args:
        order_id (int): The ID of the order.

    Returns:
        str: The order status.
    """
    logger.info(f"Retrieving status for order {order_id}.")
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
        result = cursor.fetchone()

        if result:
            return f"Your order status: {result[0]}."
        else:
            logger.warning(f"Order {order_id} not found.")
            return f"No order found with ID {order_id}."
    except Exception as e:
        logger.error(f"Error retrieving order status for order {order_id}: {e}")
        raise
    finally:
        conn.close()
