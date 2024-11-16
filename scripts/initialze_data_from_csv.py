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


def transform_row(row):
    """
    转换单行数据以匹配 `products` 表结构。

    Args:
        row (pd.Series): 单行数据。

    Returns:
        dict: 转换后的数据字典。
    """
    try:
        # 处理价格
        price_str = str(row['Selling Price']).replace("$", "").replace(",", "").strip()
        if "-" in price_str:
            low, high = price_str.split("-")
            price = (float(low.strip()) + float(high.strip())) / 2
        else:
            price = float(price_str)

        # 随机生成库存
        stock = random.choice([0, random.randint(1, 100)])

        # 生成附加规格
        additional_specs = json.dumps({
            "Product Dimensions": row['Product Dimensions'] if pd.notna(row['Product Dimensions']) else 'N/A',
            "Shipping Weight": row['Shipping Weight'] if pd.notna(row['Shipping Weight']) else 'N/A',
            "Product Specification": row['Product Specification'] if pd.notna(row['Product Specification']) else 'N/A',
        }, ensure_ascii=False)

        return {
            'name': row['Product Name'] if pd.notna(row['Product Name']) else 'Unknown',
            'description': row['About Product'] if pd.notna(row['About Product']) else 'No description available.',
            'price': price,
            'stock': stock,
            'category': row['Category'] if pd.notna(row['Category']) else 'Uncategorized',
            'image_url': row['Image'] if pd.notna(row['Image']) else None,
            'additional_specs': additional_specs
        }
    except Exception as e:
        print(f"Error transforming row: {row.to_dict()}. Error: {e}")
        return None


def insert_products_from_csv(csv_path):
    """
    从 CSV 文件逐行读取数据并插入到 `products` 表中。

    Args:
        csv_path (str): CSV 文件路径。
    """
    try:
        # 加载 CSV 数据
        df = pd.read_csv(csv_path)

        # 确保所需列存在
        required_columns = [
            'Selling Price', 'Product Name', 'Category',
            'About Product', 'Image', 'Product Dimensions',
            'Shipping Weight', 'Product Specification'
        ]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # 设置数据库路径
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        db_path = os.path.join(data_dir, "ecommerce.db")

        # 打开数据库连接
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        inserted_count = 0
        skipped_count = 0

        # 逐行处理并插入数据
        for _, row in df.iterrows():
            product = transform_row(row)
            if product is None:
                skipped_count += 1
                continue
            try:
                cursor.execute("""
                INSERT INTO products (name, description, price, stock, category, image_url, additional_specs)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    product['name'], product['description'], product['price'],
                    product['stock'], product['category'], product['image_url'],
                    product['additional_specs']
                ))
                inserted_count += 1
            except sqlite3.Error as e:
                print(f"Database error when inserting row: {product}. Error: {e}")
                skipped_count += 1

        connection.commit()
        print(f"Successfully inserted {inserted_count} products. Skipped {skipped_count} invalid rows.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if 'connection' in locals():
            connection.close()


if __name__ == "__main__":
    zip_file_path = "/path/to/your/zip_file.zip"  # Replace with actual zip file path
    extract_to_dir = "./extracted_files"  # Replace with actual extraction directory

    try:
        csv_file_path = extract_csv_from_zip(zip_file_path, extract_to_dir)
        print(f"CSV file extracted: {csv_file_path}")
        insert_products_from_csv(csv_file_path)
    except Exception as e:
        print(f"Error during processing: {e}")
