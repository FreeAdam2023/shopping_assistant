"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
import json
import sqlite3
import os
from langchain_core.tools import tool
from utils.logger import logger

# 定义数据库路径
db = os.path.join(os.path.dirname(__file__), "../data/ecommerce.db")


def checkout_order(user_id: int, address: str, payment_method: str, conn=None) -> str:
    """
    Proceed to checkout for the user's cart with a delivery address and payment method.

    Args:
        user_id (int): The ID of the user.
        address (str): The delivery address for the order.
        payment_method (str): The selected payment method for the order.
        conn: Optional database connection.

    Returns:
        str: Confirmation of the checkout process.
    """
    if not conn:
        logger.info(f"Retrieving cart contents for user {user_id}.")
        conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        # Retrieve cart contents
        cursor.execute("""
        SELECT p.id, p.price, cp.quantity, p.stock 
        FROM cart_products cp
        JOIN products p ON cp.product_id = p.id
        WHERE cp.cart_id = (
            SELECT id FROM cart WHERE user_id = ?
        )
        """, (user_id,))
        cart_contents = cursor.fetchall()

        if not cart_contents:
            logger.warning("Cart is empty.")
            return "Your cart is empty. Please add items before checking out."

        # Check stock availability
        insufficient_stock = [
            (product_id, quantity, stock)
            for product_id, price, quantity, stock in cart_contents
            if stock < quantity
        ]
        if insufficient_stock:
            issues = "\n".join(
                f"Product ID {product_id} only has {stock} in stock (requested {quantity})."
                for product_id, quantity, stock in insufficient_stock
            )
            logger.warning(f"Insufficient stock for some items: {issues}")
            return f"Checkout failed due to insufficient stock:\n{issues}"

        # Validate payment method
        valid_payment_methods = ["Credit Card", "PayPal", "Apple Pay", "Google Pay", "Bank Transfer"]
        if payment_method not in valid_payment_methods:
            logger.warning(f"Invalid payment method selected: {payment_method}.")
            return f"Invalid payment method. Available methods are: {', '.join(valid_payment_methods)}."

        # Calculate total amount
        total_amount = sum(price * quantity for _, price, quantity, _ in cart_contents)

        # Create an order with the given address and payment method
        cursor.execute("""
        INSERT INTO orders (user_id, total_amount, delivery_address, payment_method, created_at) 
        VALUES (?, ?, ?, ?, datetime('now'))
        """, (user_id, total_amount, address, payment_method))
        order_id = cursor.lastrowid

        # Insert order products and update stock
        for product_id, price, quantity, stock in cart_contents:
            cursor.execute("""
            INSERT INTO order_products (order_id, product_id, quantity, price) 
            VALUES (?, ?, ?, ?)
            """, (order_id, product_id, quantity, price))
            cursor.execute("""
            UPDATE products SET stock = stock - ? WHERE id = ?
            """, (quantity, product_id))

        # Clear the cart
        cursor.execute("""
        DELETE FROM cart_products WHERE cart_id = (
            SELECT id FROM cart WHERE user_id = ?
        )
        """, (user_id,))
        conn.commit()

        logger.info(f"Checkout complete for user {user_id}. Order ID: {order_id}.")
        return f"Checkout successful! Your order ID is {order_id}. Total amount: ${total_amount:.2f}."

    except Exception as e:
        logger.error(f"Error during checkout for user {user_id}: {e}")
        conn.rollback()
        raise
    finally:
        if not conn:
            conn.close()




def search_orders(order_id: int, conn=None) -> str:
    """
    Get the details of a specific order.

    Args:
        order_id (int): The ID of the order.
        conn
    Returns:
        str: The order details.
    """
    if not conn:
        logger.info(f"Retrieving cart contents for order {order_id}.")
        conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        # Query order information
        cursor.execute("""
        SELECT id, user_id, total_amount, status, delivery_address, cancellation_reason, created_at, updated_at 
        FROM orders
        WHERE id = ?
        """, (order_id,))
        order = cursor.fetchone()

        if not order:
            logger.warning(f"Order {order_id} not found.")
            return f"No order found with ID {order_id}."

        # Build order details
        order_details = dict(zip(
            ["Order ID", "User ID", "Total Amount", "Status", "Delivery Address", "Cancellation Reason", "Created At",
             "Updated At"],
            order
        ))

        # Query order products
        cursor.execute("""
        SELECT p.name, op.quantity, op.price 
        FROM order_products op
        JOIN products p ON op.product_id = p.id
        WHERE op.order_id = ?
        """, (order_id,))
        products = cursor.fetchall()

        order_details["Products"] = [
            {"Name": name, "Quantity": quantity, "Price": f"${price:.2f}"}
            for name, quantity, price in products
        ]

        logger.info(f"Order details retrieved successfully for order {order_id}.")
        return json.dumps(order_details, indent=4)

    except Exception as e:
        logger.error(f"Error retrieving order details for order {order_id}: {e}")
        raise
    finally:
        if not conn:
            conn.close()


def update_delivery_address(order_id: int, new_address: str, conn=None) -> str:
    """
    Update the delivery address of an order.

    Args:
        order_id (int): The ID of the order.
        new_address (str): The new delivery address.
        conn
    Returns:
        str: Confirmation of the update.
    """
    if not conn:
        logger.info(f"Updating delivery address for order {order_id}.")
        conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        # Check if the order exists
        cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
        result = cursor.fetchone()

        if not result:
            logger.warning(f"Order {order_id} not found.")
            return f"No order found with ID {order_id}."

        if result[0] in ("Shipped", "Delivered", "Cancelled"):
            logger.warning(f"Cannot update address for order {order_id} with status: {result[0]}.")
            return f"Cannot update address for order {order_id} with status: {result[0]}."

        # Update the delivery address
        cursor.execute("""
        UPDATE orders 
        SET delivery_address = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
        """, (new_address, order_id))
        conn.commit()

        logger.info(f"Delivery address updated successfully for order {order_id}.")
        return f"Delivery address for order {order_id} has been updated successfully."

    except Exception as e:
        logger.error(f"Error updating delivery address for order {order_id}: {e}")
        raise
    finally:
        if not conn:
            conn.close()


def cancel_order(order_id: int, reason: str, conn=None) -> str:
    """
    Cancel an order and provide a cancellation reason.

    Args:
        order_id (int): The ID of the order.
        reason (str): Reason for cancelling the order.
        conn
    Returns:
        str: Confirmation of the cancellation.
    """
    if not conn:
        logger.info(f"Cancelling order {order_id}.")
        conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        # Check if the order exists
        cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
        result = cursor.fetchone()

        if not result:
            logger.warning(f"Order {order_id} not found.")
            return f"No order found with ID {order_id}."

        if result[0] in ("Shipped", "Delivered", "Cancelled"):
            logger.warning(f"Cannot cancel order {order_id} with status: {result[0]}.")
            return f"Cannot cancel order {order_id} with status: {result[0]}."

        # Update the order status to "Cancelled" and record the reason
        cursor.execute("""
        UPDATE orders 
        SET status = 'Cancelled', cancellation_reason = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
        """, (reason, order_id))
        conn.commit()

        logger.info(f"Order {order_id} cancelled successfully.")
        return f"Order {order_id} has been cancelled successfully. Reason: {reason}"

    except Exception as e:
        logger.error(f"Error cancelling order {order_id}: {e}")
        raise
    finally:
        if not conn:
            conn.close()


def get_recent_orders(user_id: int, days: int = 7, conn=None) -> str:
    """
    Retrieve recent orders for a user within the specified number of days.

    Args:
        user_id (int): The ID of the user.
        days (int): The number of days to look back. Default is 7 days.
        conn
    Returns:
        str: JSON-formatted list of recent orders.
    """
    if not conn:
        logger.info(f"Retrieving recent orders for user {user_id} within the last {days} days.")
        conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        # Query orders within the specified time frame
        cursor.execute("""
        SELECT id, total_amount, status, delivery_address, created_at, updated_at 
        FROM orders 
        WHERE user_id = ? AND created_at >= datetime('now', ? || ' days')
        ORDER BY created_at DESC
        """, (user_id, f"-{days}"))
        orders = cursor.fetchall()

        if not orders:
            logger.info(f"No orders found for user {user_id} within the last {days} days.")
            return f"No recent orders found for user {user_id} within the last {days} days."

        # Build order list
        recent_orders = [
            {
                "Order ID": order[0],
                "Total Amount": f"${order[1]:.2f}",
                "Status": order[2],
                "Delivery Address": order[3],
                "Created At": order[4],
                "Updated At": order[5]
            }
            for order in orders
        ]

        logger.info(f"Found {len(recent_orders)} recent orders for user {user_id}.")
        return json.dumps(recent_orders, indent=4)

    except Exception as e:
        logger.error(f"Error retrieving recent orders for user {user_id}: {e}")
        raise
    finally:
        if not conn:
            conn.close()


@tool
def checkout_order_tool(user_id: int, address: str) -> str:
    """
    Proceed to checkout for the user's cart with a delivery address.

    Args:
        user_id (int): The ID of the user.
        address (str): The delivery address for the order.
        conn
    Returns:
        str: Confirmation of the checkout process.
    """
    return checkout_order(user_id, address)


@tool
def search_orders_tool(order_id: int) -> str:
    """
    Get the details of a specific order.

    Args:
        order_id (int): The ID of the order.

    Returns:
        str: The order details.
    """
    return search_orders(order_id)


@tool
def update_delivery_address_tool(order_id: int, new_address: str) -> str:
    """
    Update the delivery address of an order.

    Args:
        order_id (int): The ID of the order.
        new_address (str): The new delivery address.

    Returns:
        str: Confirmation of the update.
    """
    return update_delivery_address(order_id, new_address)


@tool
def cancel_order_tool(order_id: int, reason: str) -> str:
    """
    Cancel an order and provide a cancellation reason.

    Args:
        order_id (int): The ID of the order.
        reason (str): Reason for cancelling the order.

    Returns:
        str: Confirmation of the cancellation.
    """
    return cancel_order(order_id, reason)


@tool
def get_recent_orders_tool(user_id: int, days: int = 7) -> str:
    """
    Retrieve recent orders for a user within the specified number of days.

    Args:
        user_id (int): The ID of the user.
        days (int): The number of days to look back. Default is 7 days.

    Returns:
        str: JSON-formatted list of recent orders.
    """
    return get_recent_orders(user_id, days)
