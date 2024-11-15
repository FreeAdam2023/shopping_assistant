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
db = os.path.join(os.path.dirname(__file__), "../data/database.db")


@tool
def view_cart(user_id: int) -> List[Dict]:
    """
    View the contents of the user's shopping cart.

    Args:
        user_id (int): The ID of the user.

    Returns:
        List[Dict]: A list of products in the user's cart with their quantities.
    """
    logger.info(f"Retrieving cart contents for user {user_id}.")
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        query = """
        SELECT p.id, p.name, p.price, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
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
        conn.close()


@tool
def add_to_cart(user_id: int, product_id: int) -> str:
    """
    Add a product to the user's shopping cart.

    Args:
        user_id (int): The ID of the user.
        product_id (int): The ID of the product.

    Returns:
        str: Confirmation message.
    """
    logger.info(f"Adding product {product_id} to user {user_id}'s cart.")
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO cart (user_id, product_id, quantity)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + 1
            """,
            (user_id, product_id),
        )
        conn.commit()
        logger.info(f"Product {product_id} added to cart.")
        return f"Product {product_id} successfully added to your cart."
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        raise
    finally:
        conn.close()


@tool
def remove_from_cart(user_id: int, product_id: int) -> str:
    """
    Remove a product from the user's shopping cart.

    Args:
        user_id (int): The ID of the user.
        product_id (int): The ID of the product.

    Returns:
        str: Confirmation message.
    """
    logger.info(f"Removing product {product_id} from user {user_id}'s cart.")
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
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
        conn.close()
