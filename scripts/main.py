"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
from scripts.initialize_data import insert_sample_products
from scripts.initialize_db import create_database_and_tables, delete_database


def setup_database():
    delete_database()
    create_database_and_tables()
    insert_sample_products()
