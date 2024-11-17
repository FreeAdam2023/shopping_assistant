"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
import os
import sqlite3
import json
import random

# 定义更广泛的产品类别和属性
categories = {
    "Electronics": ["Smartphone", "Laptop", "Headphones", "Camera"],
    "Home Appliances": ["Microwave", "Vacuum Cleaner", "Air Conditioner", "Refrigerator"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Sweater"],
    "Food & Beverages": ["Chocolate", "Coffee", "Juice", "Snacks"],
    "Toys": ["Action Figure", "Doll", "Building Blocks", "Puzzle"],
    "Sports Equipment": ["Basketball", "Tennis Racket", "Yoga Mat", "Dumbbell"],
    "Furniture": ["Sofa", "Dining Table", "Chair", "Bookshelf"],
    "Books": ["Novel", "Cookbook", "Biography", "Textbook"]
}

# 颜色和尺寸选项
colors = ["Black", "White", "Red", "Blue", "Green", "Yellow", "None"]
sizes = ["Small", "Medium", "Large", "XL", "One Size", "None"]

# 动态生成规格
def generate_additional_specs(category, sub_category):
    if category == "Electronics":
        return {
            "Brand": random.choice(["Apple", "Samsung", "Sony", "Dell", "HP"]),
            "Warranty": f"{random.randint(1, 3)} years",
            "Feature": random.choice(["Bluetooth", "Noise Cancelling", "4K", "5G"])
        }
    elif category == "Home Appliances":
        return {
            "Energy Rating": f"{random.randint(1, 5)} stars",
            "Brand": random.choice(["Dyson", "LG", "Panasonic", "Whirlpool"]),
            "Power": f"{random.randint(500, 2000)}W"
        }
    elif category == "Clothing":
        return {
            "Material": random.choice(["Cotton", "Polyester", "Wool"]),
            "Fit": random.choice(["Regular", "Slim", "Loose"])
        }
    elif category == "Food & Beverages":
        return {
            "Brand": random.choice(["Nestle", "Coca-Cola", "Pepsi", "Kraft"]),
            "Shelf Life": f"{random.randint(6, 24)} months"
        }
    elif category == "Toys":
        return {
            "Age Group": f"{random.randint(3, 12)}+ years",
            "Material": random.choice(["Plastic", "Wood", "Metal"])
        }
    elif category == "Sports Equipment":
        return {
            "Brand": random.choice(["Adidas", "Nike", "Spalding", "Wilson"]),
            "Weight": f"{random.uniform(1, 10):.1f} kg"
        }
    elif category == "Furniture":
        return {
            "Material": random.choice(["Wood", "Metal", "Plastic"]),
            "Color Options": random.choice(["Single", "Multiple"])
        }
    elif category == "Books":
        return {
            "Author": f"Author-{random.randint(1, 100)}",
            "Pages": random.randint(100, 500)
        }
    return {}

# 插入产品数据
def insert_sample_products():
    """
    插入 200 条覆盖不同种类的产品数据到 SQLite 数据库。
    """
    try:
        # 确保 data 目录存在
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # 设置数据库路径
        db_path = os.path.join(data_dir, "ecommerce.db")
        print(f"Using database at: {db_path}")

        # 打开数据库连接
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # 检查产品表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        if not cursor.fetchone():
            raise ValueError("Table 'products' does not exist. Please initialize the database first.")

        # 生成产品数据
        products = []
        for _ in range(200):  # 创建 200 个产品
            category, sub_categories = random.choice(list(categories.items()))
            sub_category = random.choice(sub_categories)
            name = f"{sub_category} - {random.randint(1000, 9999)}"
            description = f"High-quality {sub_category} from the {category} category."
            price = round(random.uniform(10, 2000), 2)
            stock = random.choice([0, random.randint(1, 100)])
            color = random.choice(colors)
            size = random.choice(sizes)
            additional_specs = json.dumps(generate_additional_specs(category, sub_category), ensure_ascii=False)

            products.append((name, description, price, stock, category, color, size, additional_specs))

        # 批量插入产品数据
        cursor.executemany("""
        INSERT INTO products (name, description, price, stock, category, color, size, additional_specs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, products)

        # 提交事务
        connection.commit()

        print(f"Successfully inserted {len(products)} products into the database!")

        # 插入 2 条库存为 0 的产品
        zero_stock_products = [
            ("LV bag", "This is a test product with zero stock.", 99.99, 0, "Clothing", "Red", "Large", "{}"),
            ("Women Scarves", "This is another test product with zero stock.", 49.99, 0, "Clothing", "Blue", "Medium", "{}")
        ]
        cursor.executemany("""
        INSERT INTO products (name, description, price, stock, category, color, size, additional_specs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, zero_stock_products)

        print(f"Inserted {len(zero_stock_products)} products with zero stock.")

        # 提交事务
        connection.commit()

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    except ValueError as ve:
        print(f"Initialization error: {ve}")

    finally:
        # 关闭数据库连接
        if 'connection' in locals():
            connection.close()

# 执行脚本
if __name__ == "__main__":
    insert_sample_products()
