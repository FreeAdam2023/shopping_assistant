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
db = os.path.join(os.path.dirname(__file__), "../data/database.db")


@tool
def search_products(
    name: Optional[str] = None,
    category: Optional[str] = None,
    price_range: Optional[str] = None,
) -> List[Dict]:
    """
    Search for products based on name, category, and price range.

    Args:
        name (str): The product name or partial name to search for.
        category (str): The category to filter products by.
        price_range (str): A price range in the format "min-max".

    Returns:
        List[Dict]: A list of products matching the search criteria.
    """
    logger.info("Starting search_products with parameters.")
    logger.debug(f"Parameters: name={name}, category={category}, price_range={price_range}")

    try:
        # 打开数据库连接
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
                return []

        # 执行查询
        logger.debug(f"Executing query: {query} with params: {params}")
        cursor.execute(query, params)
        results = cursor.fetchall()

        # 构建结果
        products = [dict(zip([column[0] for column in cursor.description], row)) for row in results]

        logger.info(f"search_products found {len(products)} results.")
        return products

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
