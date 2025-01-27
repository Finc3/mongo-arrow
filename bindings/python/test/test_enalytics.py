# Tests implemented only for builders used by the enalytics module
#
# New tests should be added if a new build is used

from datetime import datetime, timedelta, timezone
from unittest import TestCase

from pyarrow import Array, bool_, int32, int64, timestamp

from pymongoarrow.errors import PyMongoArrowError
from pymongoarrow.lib import (
    BoolBuilder,
    Date32Builder,
    Date64Builder,
    DatetimeBuilder,
    DoubleBuilder,
    Int32Builder,
    Int64Builder,
    StringBuilder,
)


class TestBoolBuilder(TestCase):
    def test_simple(self):
        builder = BoolBuilder()
        builder.append_values([True, False])
        builder.append_null()
        arr = builder.finish()

        self.assertIsInstance(arr, Array)
        self.assertEqual(arr.null_count, 1)
        self.assertEqual(len(arr), 3)
        self.assertEqual(arr.to_pylist(), [True, False, None])
        self.assertEqual(arr.type, bool_())

    def test_invalid_type_raise(self):
        builder = BoolBuilder()
        with self.assertRaises(PyMongoArrowError):
            builder.append_values([0, 1, 1.0, "1"])


class TestDate32Builder(TestCase):
    def test_simple(self):
        values = [datetime(1970 + i, 1, 1) for i in range(3)]
        builder = Date32Builder()
        builder.append(values[0])
        builder.append_values(values[1:])
        builder.append_null()
        arr = builder.finish()

        self.assertIsInstance(arr, Array)
        self.assertEqual(arr.null_count, 1)
        self.assertEqual(len(arr), 4)
        dates = [v.date() for v in values]
        self.assertEqual(arr.to_pylist(), dates + [None])

    def test_invalid_type_raise(self):
        builder = Date32Builder()
        with self.assertRaises(PyMongoArrowError):
            builder.append_values([0, 1, True, "2025-01-01"])


class TestDate64Builder(TestCase):
    def test_simple(self):
        values = [datetime(1970 + i, 1, 1) for i in range(3)]
        builder = Date64Builder()
        builder.append(values[0])
        builder.append_values(values[1:])
        builder.append_null()
        arr = builder.finish()

        self.assertIsInstance(arr, Array)
        self.assertEqual(arr.null_count, 1)
        self.assertEqual(len(arr), 4)
        dates = [v.date() for v in values]
        self.assertEqual(arr.to_pylist(), dates + [None])

    def test_invalid_type_raise(self):
        builder = Date64Builder()
        with self.assertRaises(PyMongoArrowError):
            builder.append_values([0, 1, True, "2025-01-01"])


class TestDatetimeBuilder(TestCase):
    def test_simple(self):
        self.maxDiff = None

        builder = DatetimeBuilder(dtype=timestamp("ms"))
        datetimes = [datetime.now(timezone.utc) + timedelta(days=k * 100) for k in range(5)]
        builder.append(datetimes[0])
        builder.append_values(datetimes[1:])
        builder.append_null()
        arr = builder.finish()

        self.assertIsInstance(arr, Array)
        self.assertEqual(arr.null_count, 1)
        self.assertEqual(len(arr), len(datetimes) + 1)
        for actual, expected in zip(arr, datetimes + [None]):
            if actual.is_valid:
                self.assertEqual(actual.as_py().timetuple(), expected.timetuple())
            else:
                self.assertIsNone(expected)
        self.assertEqual(arr.type, timestamp("ms"))

    def test_invalid_type_raise(self):
        builder = DatetimeBuilder()
        with self.assertRaises(PyMongoArrowError):
            builder.append_values([0, 1, True, "2025-01-01T00:00:00Z"])


class TestDoubleBuilder(TestCase):
    def test_simple(self):
        builder = DoubleBuilder()
        values = [0.123, 1.234, 2.345, 3.456, 4.567, 1]
        builder.append(values[0])
        builder.append_values(values[1:])
        builder.append_null()
        arr = builder.finish()

        self.assertIsInstance(arr, Array)
        self.assertEqual(arr.null_count, 1)
        self.assertEqual(len(arr), 7)
        self.assertEqual(arr.to_pylist(), values + [None])

    def test_invalid_type_raise(self):
        builder = DoubleBuilder()
        with self.assertRaises(PyMongoArrowError):
            builder.append_values([True, "0", "1.1"])


class TestInt32Builder(TestCase):
    def test_simple(self):
        builder = Int32Builder()
        builder.append(0)
        builder.append_values([1, 2, 3, 4])
        builder.append_null()
        arr = builder.finish()

        self.assertIsInstance(arr, Array)
        self.assertEqual(arr.null_count, 1)
        self.assertEqual(len(arr), 6)
        self.assertEqual(arr.to_pylist(), [0, 1, 2, 3, 4, None])
        self.assertEqual(arr.type, int32())

    def test_invalid_type_raise(self):
        builder = Int32Builder()
        with self.assertRaises(PyMongoArrowError):
            builder.append_values([True, "1", "1.1"])


class TestInt64Builder(TestCase):
    def test_simple(self):
        builder = Int64Builder()
        builder.append(0)
        builder.append_values([1, 2, 3, 4])
        builder.append_null()
        arr = builder.finish()

        self.assertIsInstance(arr, Array)
        self.assertEqual(arr.null_count, 1)
        self.assertEqual(len(arr), 6)
        self.assertEqual(arr.to_pylist(), [0, 1, 2, 3, 4, None])
        self.assertEqual(arr.type, int64())

    def test_invalid_type_raise(self):
        builder = Int64Builder()
        with self.assertRaises(PyMongoArrowError):
            builder.append_values([True, "1", "1.1"])


class TestStringBuilder(TestCase):
    def test_simple(self):
        # Greetings in various languages, from
        # https://www.w3.org/2001/06/utf-8-test/UTF-8-demo.html
        values = ["Hello world", "Καλημέρα κόσμε", "コンニチハ"]
        values += ["hello\u0000world"]
        builder = StringBuilder()
        builder.append(values[0])
        builder.append_values(values[1:])
        builder.append_null()
        arr = builder.finish()

        self.assertIsInstance(arr, Array)
        self.assertEqual(arr.null_count, 1)
        self.assertEqual(len(arr), 5)
        self.assertEqual(arr.to_pylist(), values + [None])

    def test_invalid_type_raise(self):
        builder = StringBuilder()
        with self.assertRaises(PyMongoArrowError):
            builder.append_values([0, 1, True, 1.1, b"1"])
