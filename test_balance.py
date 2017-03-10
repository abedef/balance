#!/Library/FrameWorks/Python.framework/Versions/3.5/bin/python3

from balance import TransactionManager
from balance import Transaction
import os
import unittest


class TestTransaction(unittest.TestCase):
    def test_constructor_positive_simple(self):
        t = Transaction(100, [])
        self.assertEqual(t.is_negative, False)
        self.assertEqual(t.dollars, 100)
        self.assertEqual(t.cents, 0)

    def test_constructor_negative_simple(self):
        t = Transaction(-100, [])
        self.assertEqual(t.is_negative, True)
        self.assertEqual(t.dollars, 100)
        self.assertEqual(t.cents, 0)

    def test_constructor_positive_small(self):
        t = Transaction(100.01, [])
        self.assertEqual(t.is_negative, False)
        self.assertEqual(t.dollars, 100)
        self.assertEqual(t.cents, 1)

    def test_constructor_positive_big(self):
        t = Transaction(100.99, [])
        self.assertEqual(t.is_negative, False)
        self.assertEqual(t.dollars, 100)
        self.assertEqual(t.cents, 99)

    def test_constructor_negative_small(self):
        t = Transaction(-100.99, [])
        self.assertEqual(t.is_negative, True)
        self.assertEqual(t.dollars, 100)
        self.assertEqual(t.cents, 99)

    def test_constructor_negative_big(self):
        t = Transaction(-100.01, [])
        self.assertEqual(t.is_negative, True)
        self.assertEqual(t.dollars, 100)
        self.assertEqual(t.cents, 1)

    def test_string_positive_simple(self):
        t = Transaction(100.01, [])
        t.date = t.date.replace(1995, 12, 12)
        self.assertEqual(str(t), "100.01 on 1995-12-12")

    def test_string_negative_simple(self):
        t = Transaction(-100.01, [])
        t.date = t.date.replace(1995, 12, 12)
        self.assertEqual(str(t), "-100.01 on 1995-12-12")

    def test_string_complex(self):
        t = Transaction(100, ["birthday", "toy"])
        t.date = t.date.replace(1995, 12, 12)
        self.assertEqual(str(t), "100.00 on 1995-12-12 #birthday #toy")


class TestTransactionManager(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
