import os
import sqlite3


def create_tables(cursor):
    """
    创建表结构。
    Args:
        cursor: SQLite 游标对象
    """
    # 创建产品表
    cursor.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
        category TEXT NOT NULL,
        color TEXT DEFAULT NULL,
        size TEXT DEFAULT NULL,
        additional_specs TEXT DEFAULT NULL,
        image_url TEXT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 创建购物车表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 创建购物车产品表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (cart_id) REFERENCES cart (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    );
    """)

    # 创建订单表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, -- 订单ID
        user_id INTEGER NOT NULL, -- 用户ID
        total_amount REAL NOT NULL, -- 订单总金额
        status TEXT CHECK(status IN ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled')) DEFAULT 'Pending', -- 订单状态
        delivery_address TEXT DEFAULT NULL, -- 交货地址
        payment_method TEXT NOT NULL, -- 付款方式
        cancellation_reason TEXT DEFAULT NULL, -- 取消原因
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 订单创建时间
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 订单更新时间
    );
    """)

    # 创建订单产品表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL, -- 记录购买时的单价
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    );
    """)


def create_database_and_tables(db_path=None):
    """
    创建 SQLite 数据库及相关表。如果文件不存在，将会自动创建。
    Args:
        db_path (str): 数据库文件路径，默认保存在 ../data/ecommerce.db。
    """
    try:
        # 默认路径为 ../data/ecommerce.db
        if not db_path:
            data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            db_path = os.path.join(data_dir, "ecommerce.db")

        # 打开 SQLite 数据库连接
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # 创建表结构
        create_tables(cursor)

        # 提交事务
        connection.commit()
        print(f"Database and tables created successfully! Database path: {db_path}")

    except sqlite3.Error as e:
        print(f"An error occurred while creating database or tables: {e}")
        raise

    finally:
        if connection:
            connection.close()


def delete_database(db_path=None):
    """
    删除 SQLite 数据库文件。
    Args:
        db_path (str): 数据库文件路径，默认删除 ../data/ecommerce.db。
    """
    try:
        # 默认路径为 ../data/ecommerce.db
        if not db_path:
            data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
            db_path = os.path.join(data_dir, "ecommerce.db")

        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Database deleted successfully! Path: {db_path}")
        else:
            print(f"Database file does not exist at: {db_path}")

    except Exception as e:
        print(f"An error occurred while deleting the database: {e}")
        raise


if __name__ == "__main__":
    # 删除生产数据库
    delete_database()

    # 创建生产数据库
    create_database_and_tables()

    # 创建测试数据库
    # test_conn = create_test_database_and_tables()
    # cursor = test_conn.cursor()
    # cursor.execute("INSERT INTO products (name, price, stock, category) VALUES (?, ?, ?, ?)",
    #                ("Test Product", 10.99, 100, "Test Category"))
    # test_conn.commit()
    #
    # cursor.execute("SELECT * FROM products;")
    # print("Test Database Products:", cursor.fetchall())
