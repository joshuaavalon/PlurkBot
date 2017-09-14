from unittest import TestCase
from plurk_bot.utils import *


class UtilsTest(TestCase):
    def test_check_type(self):
        self.assertEqual(check_type(1, int), 1)
        self.assertEqual(check_type(1, [int, str]), 1)
        self.assertEqual(check_type(1, [str]), None)
        self.assertEqual(check_type(1, str), None)
        self.assertEqual(check_type(1, int, 2), 1)
        self.assertEqual(check_type(1, [int, str], 2), 1)
        self.assertEqual(check_type(1, [str], 2), 2)
        self.assertEqual(check_type(1, str, 2), 2)
        self.assertEqual(check_type(1, None, 2), 2)
        self.assertEqual(check_type(None, None), None)
        self.assertEqual(check_type(None, None, 2), 2)
        self.assertEqual(check_type(None, type(None)), None)

    # noinspection PyTypeChecker
    def test_try_get(self):
        test_dict = {1: 2}
        self.assertEqual(try_get(1, 1), None)
        self.assertEqual(try_get(1, 1, 2), 2)
        self.assertEqual(try_get(test_dict, 1), 2)
        self.assertEqual(try_get(test_dict, 2), None)
        self.assertEqual(try_get(test_dict, 2, 3), 3)


class CatchAndLogTest(TestCase):
    def test_call(self):
        self.raise_error()
        with self.assertRaises(RuntimeError):
            self.raise_error_rethrow()
        self.assertEqual(self.raise_error_default(), 1)
        with self.assertRaises(RuntimeError):
            self.raise_error_rethrow_default()

    @CatchAndLog()
    def raise_error(self):
        raise RuntimeError()

    @CatchAndLog(rethrow=True)
    def raise_error_rethrow(self):
        raise RuntimeError()

    @CatchAndLog(default=1)
    def raise_error_default(self):
        raise RuntimeError()

    @CatchAndLog(rethrow=True, default=1)
    def raise_error_rethrow_default(self):
        raise RuntimeError()
