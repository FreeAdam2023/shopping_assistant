"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
import os
import sqlite3
import pandas as pd
import zipfile
import json
import random


def extract_csv_from_zip(zip_path, extract_to):
    """
    解压 zip 文件中的 CSV 文件。

    Args:
        zip_path (str): zip 文件路径。
        extract_to (str): 解压到的目录。

    Returns:
        str: 解压后的 CSV 文件路径。
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            print(f"Extracted files to: {extract_to}")
            for file in os.listdir(extract_to):
                if file.endswith('.csv'):
                    return os.path.join(extract_to, file)
        raise FileNotFoundError("No CSV file found in the zip archive.")
    except Exception as e:
        print(f"Error extracting zip file: {e}")
        raise


def create_products_table(db_path):
    """
    创建或更新 products 表。

    Args:
        db_path (str): SQLite 数据库路径。
    """
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            category TEXT NOT NULL,
            color TEXT DEFAULT NULL,
            size TEXT DEFAULT NULL,
            additional_specs TEXT DEFAULT NULL, -- 使用 JSON 格式存储动态规格
            image_url TEXT DEFAULT NULL, -- 存储产品图片 URL
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        connection.commit()
        print("Products table created successfully!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'connection' in locals():
            connection.close()


def transform_data(df):
    """
    转换数据以匹配 `products` 表的结构。

    Args:
        df (pd.DataFrame): 原始数据。

    Returns:
        pd.DataFrame: 转换后的数据。
    """

    # 处理价格（移除美元符号并处理价格范围为平均值）
    def parse_price(price):
        try:
            # 如果价格是单个值
            if "-" not in price:
                return float(price.replace("$", "").strip())
            # 如果价格是范围值，取平均值
            low, high = price.split("-")
            return (float(low.replace("$", "").strip()) + float(high.replace("$", "").strip())) / 2
        except Exception:
            return 0.0  # 对于异常情况，默认值为 0.0

    # 清洗数据
    df['price'] = df['Selling Price'].apply(parse_price)

    # 随机生成库存，包括一些库存为 0 的值
    df['stock'] = [random.choice([0, random.randint(1, 100)]) for _ in range(len(df))]

    # 填充缺失值
    df['Category'] = df['Category'].fillna("Uncategorized")
    df['About Product'] = df['About Product'].fillna("No description available.")
    df['Image'] = df['Image'].fillna(None)

    # 生成 additional_specs 字段（动态 JSON 数据）
    df['additional_specs'] = df.apply(lambda row: json.dumps({
        "Product Dimensions": row['Product Dimensions'] if pd.notna(row['Product Dimensions']) else 'N/A',
        "Shipping Weight": row['Shipping Weight'] if pd.notna(row['Shipping Weight']) else 'N/A',
        "Product Specification": row['Product Specification'] if pd.notna(row['Product Specification']) else 'N/A',
    }), axis=1)

    # 选择需要的字段
    transformed_df = df.rename(columns={
        'Product Name': 'name',
        'About Product': 'description',
        'Category': 'category',
        'Image': 'image_url'
    })[['name', 'description', 'price', 'stock', 'category', 'image_url', 'additional_specs']]

    return transformed_df


def insert_products_from_csv(csv_path):
    """
    从 CSV 文件读取数据并插入到 `products` 表中。

    Args:
        csv_path (str): CSV 文件路径。
    """
    try:
        # 加载 CSV 数据
        df = pd.read_csv(csv_path)

        # 转换数据
        transformed_df = transform_data(df)

        # 设置数据库路径
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        db_path = os.path.join(data_dir, "ecommerce.db")

        # 打开数据库连接
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # 插入数据
        products = transformed_df.values.tolist()
        cursor.executemany("""
        INSERT INTO products (name, description, price, stock, category, image_url, additional_specs)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, products)

        connection.commit()
        print(f"Successfully inserted {len(products)} products into the database!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if 'connection' in locals():
            connection.close()


if __name__ == "__main__":
    # 文件路径设置
    zip_file_path = "/path/to/your/zip_file.zip"  # 替换为你的 zip 文件路径
    extract_to_dir = "./extracted_files"  # 替换为你想要解压到的目录

    try:
        # 解压 CSV 文件
        csv_file_path = extract_csv_from_zip(zip_file_path, extract_to_dir)
        print(f"CSV file extracted: {csv_file_path}")

        # 创建数据库表
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
        db_path = os.path.join(data_dir, "ecommerce.db")
        create_products_table(db_path)

        # 插入数据到数据库
        insert_products_from_csv(csv_file_path)
    except Exception as e:
        print(f"Error during processing: {e}")
