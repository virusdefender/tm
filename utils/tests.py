# coding=utf-8
from decimal import Decimal

from django.test import TestCase

from .shortcuts import decimal_round


class DecimalRoundTest(TestCase):

    def setUp(self):
        pass

    def test_1(self):
        self.assertEqual(Decimal("1"), decimal_round(Decimal("1")))
        self.assertEqual(Decimal("1.0"), decimal_round(Decimal("1.0")))
        self.assertEqual(Decimal("1.21"), decimal_round(Decimal("1.21")))
        self.assertEqual(Decimal("1.21"), decimal_round(Decimal("1.214")))
        self.assertEqual(Decimal("1.21"), decimal_round(Decimal("1.216")))
        self.assertEqual(Decimal("0.05"), decimal_round(Decimal("0.05")))
