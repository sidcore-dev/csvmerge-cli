import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from csvmerge_cli.cli import main


class TestCli(unittest.TestCase):
    def test_merges_two_files_to_stdout(self) -> None:
        with TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            a.write_text("id,name\n1,Alice\n")
            b.write_text("id,name\n2,Bob\n")
            out = io.StringIO()
            with redirect_stdout(out):
                code = main([str(a), str(b)])
            self.assertEqual(code, 0)
            self.assertEqual(out.getvalue(), "id,name\r\n1,Alice\r\n2,Bob\r\n")

    def test_writes_to_out_file(self) -> None:
        with TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            out_path = Path(tmp) / "out.csv"
            a.write_text("id,name\n1,Alice\n")
            b.write_text("id,name\n2,Bob\n")
            code = main([str(a), str(b), "--out", str(out_path)])
            self.assertEqual(code, 0)
            content = out_path.read_text()
            self.assertIn("1,Alice", content)
            self.assertIn("2,Bob", content)

    def test_mismatched_headers_errors_and_exits_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            a.write_text("id,name\n1,Alice\n")
            b.write_text("id,email\n2,bob@x.com\n")
            err = io.StringIO()
            with redirect_stderr(err):
                code = main([str(a), str(b)])
            self.assertEqual(code, 1)
            self.assertIn("does not match", err.getvalue())

    def test_allow_reorder_flag_permits_reordered_columns(self) -> None:
        with TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            a.write_text("id,name\n1,Alice\n")
            b.write_text("name,id\nBob,2\n")
            out = io.StringIO()
            with redirect_stdout(out):
                code = main([str(a), str(b), "--allow-reorder"])
            self.assertEqual(code, 0)
            self.assertIn("2,Bob", out.getvalue())

    def test_missing_file_errors_with_exit_code_two(self) -> None:
        err = io.StringIO()
        with redirect_stderr(err):
            code = main(["/no/such/file.csv"])
        self.assertEqual(code, 2)
        self.assertIn("could not read", err.getvalue())


if __name__ == "__main__":
    unittest.main()
