"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
from scripts.initialize_data import insert_sample_products
from scripts.initialize_db import create_database_and_tables, delete_database
from scripts.initialze_data_from_csv import insert_products_from_csv, extract_csv_from_zip


def setup_database():
    delete_database()
    create_database_and_tables()
    # csv_file_path = extract_csv_from_zip(
    #     'marketing_sample_for_amazon_com-ecommerce__20200101_20200131__10k_data.csv.zip', '.')
    csv_file_path = 'marketing_sample_for_amazon_com-ecommerce__20200101_20200131__10k_data.csv'
    insert_products_from_csv(csv_file_path)


if __name__ == "__main__":
    setup_database()
