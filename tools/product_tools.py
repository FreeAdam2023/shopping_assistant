"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
from typing import Optional, List, Dict
from langchain_core.tools import tool
import sqlite3
import os
from utils.logger import logger

# 定义数据库路径
db = os.path.join(os.path.dirname(__file__), "../data/ecommerce.db")


def list_categories(conn=None) -> List[str]:
    """
    List all available product categories in the database.

    Returns:
        List[str]: A list of unique product categories.
    """
    logger.info("Starting list_categories tool.")

    try:
        # 打开数据库连接
        if not conn:
            conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # 查询所有类别
        query = "SELECT DISTINCT category FROM products WHERE category IS NOT NULL"
        logger.debug(f"Executing query: {query}")
        cursor.execute(query)
        results = cursor.fetchall()

        # 提取类别名称
        categories = [row[0] for row in results]
        logger.info(f"Found {len(categories)} categories.")
        return categories

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return []

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []

    finally:
        # 确保关闭连接
        if 'conn' in locals():
            conn.close()


def search_and_recommend_products(
        name: Optional[str] = None,
        category: Optional[str] = None,
        price_range: Optional[str] = None,
        conn=None,
) -> Dict[str, List[Dict]]:
    """
    Search for products based on name, category, and price range, and recommend related products.

    Args:
        name (str): The product name or partial name to search for.
        category (str): The category to filter products by.
        price_range (str): A price range in the format "min-max".
        conn
    Returns:
        Dict[str, List[Dict]]: A dictionary with search results and recommendations.
    """
    logger.info("Starting search_and_recommend_products with parameters.")
    logger.debug(f"Parameters: name={name}, category={category}, price_range={price_range}")

    try:
        # 打开数据库连接
        if not conn:
            conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # 构建查询
        query = "SELECT * FROM products WHERE 1=1"
        params = []

        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if category:
            query += " AND category = ?"
            params.append(category)
        if price_range:
            try:
                min_price, max_price = map(float, price_range.split('-'))
                query += " AND price BETWEEN ? AND ?"
                params.extend([min_price, max_price])
            except ValueError:
                logger.error("Invalid price_range format. Expected format is 'min-max'.")
                return {"search_results": [], "recommendations": []}

        # 执行查询
        logger.debug(f"Executing query: {query} with params: {params}")
        cursor.execute(query, params)
        results = cursor.fetchall()

        # 构建结果
        products = [dict(zip([column[0] for column in cursor.description], row)) for row in results]

        # 如果没有找到产品，则不执行推荐逻辑
        if not products:
            logger.info("No products found. Skipping recommendation.")
            return {"search_results": [], "recommendations": []}

        # 推荐系统：基于类别和价格范围推荐替代产品
        recommendations_query = """
        SELECT * FROM products 
        WHERE category = ? 
        AND price BETWEEN ? AND ? 
        AND name NOT LIKE ? 
        LIMIT 5
        """
        # 推荐的价格范围为原价格上下浮动 20%
        recommended_params = [
            category or products[0]["category"],
            products[0]["price"] * 0.8,
            products[0]["price"] * 1.2,
            f"%{name or ''}%"
        ]
        logger.debug(f"Executing recommendation query: {recommendations_query} with params: {recommended_params}")
        cursor.execute(recommendations_query, recommended_params)
        recommendations_results = cursor.fetchall()
        recommendations = [
            dict(zip([column[0] for column in cursor.description], row)) for row in recommendations_results
        ]

        logger.info(
            f"search_and_recommend_products found {len(products)} search results and {len(recommendations)} recommendations.")
        return {"search_results": products, "recommendations": recommendations}

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return {"search_results": [], "recommendations": []}

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"search_results": [], "recommendations": []}

    finally:
        # 确保关闭连接
        if 'conn' in locals():
            conn.close()



def check_product_stock(product_id: int, conn=None) -> Optional[Dict]:
    """
    Check the stock information of a specific product.

    Args:
        product_id (int): The ID of the product to check.
        conn: SQLite database connection.

    Returns:
        Optional[Dict]: A dictionary containing product stock information or None if not found.
    """
    logger.info(f"Checking stock for product {product_id}.")

    try:
        # 打开数据库连接
        if not conn:
            conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # 查询产品库存信息
        query = """
        SELECT id, name, category, stock
        FROM products
        WHERE id = ?
        """
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()

        if result:
            # 返回库存信息
            product_stock_info = dict(zip([column[0] for column in cursor.description], result))
            logger.info(f"Found stock information for product {product_id}: {product_stock_info}")
            return product_stock_info
        else:
            logger.warning(f"No stock information found for product {product_id}.")
            return None

    except sqlite3.Error as e:
        logger.error(f"Database error while checking stock for product {product_id}: {e}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error while checking stock for product {product_id}: {e}")
        return None

    finally:
        if not conn:
            conn.close()


@tool
def list_categories_tool() -> List[str]:
    """
    List all available product categories in the database.

    Returns:
        List[str]: A list of unique product categories.
    """
    return list_categories()


@tool
def search_and_recommend_products_tool(name: Optional[str] = None, category: Optional[str] = None,
                                       price_range: Optional[str] = None) -> Dict[str, List[Dict]]:
    """
        Search for products based on name, category, and price range, and recommend related products.

        Args:
            name (str): The product name or partial name to search for.
            category (str): The category to filter products by.
            price_range (str): A price range in the format "min-max".

        Returns:
            Dict[str, List[Dict]]: A dictionary with search results and recommendations.
        """
    return search_and_recommend_products(name, category, price_range)

#
# @tool
# def update_stock_on_cancellation_tool(order_id: int, conn=None):
#     """
#     Restore product stock when an order is cancelled.
#
#     Args:
#         order_id (int): The ID of the cancelled order.
#         conn: SQLite database connection.
#     """
#     return update_stock_on_cancellation(order_id, conn)
#
#
# @tool
# def update_stock_on_order_tool(order_id: int, conn=None):
#     """
#     Update product stock when an order is activated or completed.
#
#     Args:
#         order_id (int): The ID of the order.
#         conn: SQLite database connection.
#     """
#     return update_stock_on_order(order_id, conn)


@tool
def check_product_stock_tool(product_id: int, conn=None) -> Optional[Dict]:
    """
    Check the stock information of a specific product.

    Args:
        product_id (int): The ID of the product to check.
        conn: SQLite database connection.

    Returns:
        Optional[Dict]: A dictionary containing product stock information or None if not found.
    """
    return check_product_stock(product_id, conn)
