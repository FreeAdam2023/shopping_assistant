"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
import unittest
from tools.cart_tools import add_to_cart, view_cart
from scripts.initialize_db import initialize_db

class TestCartTools(unittest.TestCase):
    def setUp(self):
        initialize_db()

    def test_add_to_cart(self):
        response = add_to_cart(user_id=1, product_id=101, quantity=2)
        self.assertIn("Added product", response)

    def test_view_cart(self):
        add_to_cart(user_id=1, product_id=101, quantity=2)
        items = view_cart(user_id=1)
        self.assertGreater(len(items), 0)

if __name__ == "__main__":
    unittest.main()
