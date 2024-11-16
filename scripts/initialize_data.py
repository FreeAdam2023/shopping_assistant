"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
import sqlite3
import random
import json

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

colors = ["Black", "White", "Red", "Blue", "Green", "Yellow", "None"]
sizes = ["Small", "Medium", "Large", "XL", "One Size", "None"]

# 动态生成规格
def generate_additional_specs(category, sub_category):
    if category == "Electronics":
        return {
            "Brand": random.choice(["BrandA", "BrandB", "BrandC"]),
            "Warranty": f"{random.randint(1, 3)} years",
            "Feature": random.choice(["Bluetooth", "Noise Cancelling", "4K"])
        }
    elif category == "Home Appliances":
        return {
            "Energy Rating": f"{random.randint(1, 5)} stars",
            "Brand": random.choice(["BrandX", "BrandY", "BrandZ"]),
            "Power": f"{random.randint(500, 2000)}W"
        }
    elif category == "Clothing":
        return {
            "Material": random.choice(["Cotton", "Polyester", "Wool"]),
            "Fit": random.choice(["Regular", "Slim", "Loose"])
        }
    elif category == "Food & Beverages":
        return {
            "Brand": random.choice(["BrandF", "BrandG"]),
            "Shelf Life": f"{random.randint(6, 24)} months"
        }
    elif category == "Toys":
        return {
            "Age Group": f"{random.randint(3, 12)}+ years",
            "Material": random.choice(["Plastic", "Wood"])
        }
    elif category == "Sports Equipment":
        return {
            "Brand": random.choice(["BrandS1", "BrandS2"]),
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

# 插入数据
def insert_sample_products():
    try:
        # 连接到 SQLite 数据库
        connection = sqlite3.connect("ecommerce.db")
        cursor = connection.cursor()

        # 插入 1000 个随机产品
        products = []
        for _ in range(1000):
            category, sub_categories = random.choice(list(categories.items()))
            sub_category = random.choice(sub_categories)
            name = f"{sub_category} - {random.randint(1000, 9999)}"
            description = f"A high-quality {sub_category} from the {category} category."
            price = round(random.uniform(5, 5000), 2)
            stock = random.randint(1, 500)
            color = random.choice(colors)
            size = random.choice(sizes)
            additional_specs = json.dumps(generate_additional_specs(category, sub_category))

            products.append((name, description, price, stock, category, color, size, additional_specs))

        # 批量插入产品数据
        cursor.executemany("""
        INSERT INTO products (name, description, price, stock, category, color, size, additional_specs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, products)

        # 提交事务
        connection.commit()

        print(f"Successfully inserted {len(products)} diverse products into the database!")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        # 关闭数据库连接
        if connection:
            connection.close()

# 执行脚本
if __name__ == "__main__":
    insert_sample_products()
