import os
import sqlite3


def create_database_and_tables():
    try:
        # 确保 data 目录存在
        data_dir = "../data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        # 设置数据库路径
        db_path = os.path.join(data_dir, "ecommerce.db")
        connection = sqlite3.connect(db_path)
        # 创建游标对象
        cursor = connection.cursor()

        # 创建产品表
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 创建购物车表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 创建购物车产品表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (cart_id) REFERENCES cart(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
        """)

        # 创建订单表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT CHECK(status IN ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled')) DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 创建订单产品表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL, -- 记录购买时的单价
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
        """)

        # 提交事务
        connection.commit()

        print("Database and tables created successfully!")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        # 关闭数据库连接
        if connection:
            connection.close()


# 执行脚本
if __name__ == "__main__":
    create_database_and_tables()
