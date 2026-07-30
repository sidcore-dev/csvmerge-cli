import unittest

from csvmerge_cli.core import HeaderMismatchError, Table, merge_tables, reorder_row


class TestReorderRow(unittest.TestCase):
    def test_reorders_values_to_match_target_header(self) -> None:
        row = ["Bob", "2", "20"]
        from_header = ["name", "id", "amount"]
        to_header = ["id", "name", "amount"]
        self.assertEqual(reorder_row(row, from_header, to_header), ["2", "Bob", "20"])


class TestMergeTables(unittest.TestCase):
    def test_merges_matching_headers(self) -> None:
        a = Table("a.csv", ["id", "name"], [["1", "Alice"]])
        b = Table("b.csv", ["id", "name"], [["2", "Bob"]])
        header, rows = merge_tables([a, b])
        self.assertEqual(header, ["id", "name"])
        self.assertEqual(rows, [["1", "Alice"], ["2", "Bob"]])

    def test_rejects_mismatched_columns_by_default(self) -> None:
        a = Table("a.csv", ["id", "name"], [["1", "Alice"]])
        b = Table("b.csv", ["name", "id"], [["Bob", "2"]])
        with self.assertRaises(HeaderMismatchError) as ctx:
            merge_tables([a, b])
        self.assertIn("b.csv", str(ctx.exception))

    def test_rejects_genuinely_different_columns_even_with_reorder(self) -> None:
        a = Table("a.csv", ["id", "name"], [["1", "Alice"]])
        b = Table("b.csv", ["id", "email"], [["2", "bob@x.com"]])
        with self.assertRaises(HeaderMismatchError):
            merge_tables([a, b], allow_reorder=True)

    def test_allow_reorder_permits_and_fixes_column_order(self) -> None:
        a = Table("a.csv", ["id", "name"], [["1", "Alice"]])
        b = Table("b.csv", ["name", "id"], [["Bob", "2"]])
        header, rows = merge_tables([a, b], allow_reorder=True)
        self.assertEqual(header, ["id", "name"])
        self.assertEqual(rows, [["1", "Alice"], ["2", "Bob"]])

    def test_single_table_returns_its_own_rows(self) -> None:
        a = Table("a.csv", ["id"], [["1"], ["2"]])
        header, rows = merge_tables([a])
        self.assertEqual(header, ["id"])
        self.assertEqual(rows, [["1"], ["2"]])

    def test_empty_table_list_returns_empty(self) -> None:
        header, rows = merge_tables([])
        self.assertEqual(header, [])
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
