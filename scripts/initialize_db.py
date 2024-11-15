"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
import pandas as pd
import sqlite3
from zipfile import ZipFile

# 文件路径
zip_file_path = "marketing_sample_for_amazon_com-ecommerce__20200101_20200131__10k_data.csv.zip"
extracted_file_path = "marketing_sample_for_amazon_com-ecommerce__20200101_20200131__10k_data.csv"
database_path = "shopping_assistant.db"

# 解压缩文件
with ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall()

# 加载 CSV 文件
data = pd.read_csv(extracted_file_path)

# 清理和准备数据
data_cleaned = data[['Product Name', 'Category', 'Selling Price', 'Stock']].copy()

# 重命名字段以匹配数据库字段
data_cleaned.rename(columns={
    'Product Name': 'name',
    'Category': 'category',
    'Selling Price': 'price',
    'Stock': 'stock'
}, inplace=True)


# 提取最低价格
def extract_min_price(price):
    try:
        if '-' in str(price):  # 如果价格是范围，提取最小值
            return float(price.split('-')[0].strip())
        return float(price.replace('$', '').strip())  # 处理单一价格
    except ValueError:
        return None


data_cleaned['price'] = data_cleaned['price'].apply(extract_min_price)

# 删除无效数据
data_cleaned.dropna(subset=['name', 'category', 'price'], inplace=True)

# 填充缺失库存值
data_cleaned['stock'] = data_cleaned['stock'].fillna(10).astype(int)

# 连接 SQLite 数据库
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# 创建 `products` 表
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL
);
""")

# 创建 `cart` 表
cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    UNIQUE(user_id, product_id)
);
""")

# 创建 `orders` 表
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT DEFAULT 'Processing'
);
""")

# 创建 `order_details` 表
cursor.execute("""
CREATE TABLE IF NOT EXISTS order_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL
);
""")

# 限制每个类别的插入数量
category_count = {}
total_inserted = 0  # 记录插入成功的总数

# 插入清理后的数据到 `products` 表
for _, row in data_cleaned.iterrows():
    category = row['category']

    # 初始化类别计数
    if category not in category_count:
        category_count[category] = 0

    # 检查是否达到限制
    if category_count[category] < 10:
        cursor.execute("""
        INSERT INTO products (name, category, price, stock) 
        VALUES (?, ?, ?, ?);
        """, (row['name'], row['category'], row['price'], row['stock']))
        category_count[category] += 1
        total_inserted += 1  # 增加总插入计数

# 提交更改并关闭数据库连接
conn.commit()
conn.close()

# 打印结果
print("Inserted products by category:")
for category, count in category_count.items():
    print(f"{category}: {count} products")

print(f"Total products inserted: {total_inserted}")
