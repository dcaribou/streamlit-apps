"""Unit tests for my utils.py module.
"""

from utils.financial import mortgage_principal_contribution, mortgage_monthly_payment
import unittest

class TestUtils(unittest.TestCase):

    def test_mortgage_payment(self):
        self.assertEqual(
            round(mortgage_monthly_payment(0.03, 100000, 30), 2),
            421.60
        )

    def test_mortgage_principal(self):
        # from example
        # https://math.libretexts.org/Bookshelves/Applied_Mathematics/Business_Math_(Olivier)/13%3A_Understanding_Amortization_and_its_Applications/13.01%3A_Calculating_Interest_and_Principal_Components
        principal = 409.417128
        interest = 42.612871
        self.assertEqual(
            round(mortgage_principal_contribution(0.08, principal + interest, 10, 2), 2),
            principal
        )
