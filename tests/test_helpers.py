import unittest
import logging
from unittest.mock import patch

from modules import helpers


class TestHelpers(unittest.TestCase):
    def test_is_valid_filename(self) -> None:
        filename: str = "my_file.txt"
        filename_template: str = r"^[a-z_]*.txt$"
        result: bool = helpers.is_valid_filename(
            filename=filename,
            filename_template=filename_template,
        )
        expected: bool = True
        self.assertEqual(result, expected)

    def test_is_valid_filename_neq(self) -> None:
        filename: str = "my_file.txt"
        filename_template: str = r"^[a-z_]$"
        result: bool = helpers.is_valid_filename(
            filename=filename,
            filename_template=filename_template,
        )
        expected: bool = True
        self.assertNotEqual(result, expected)

    def test_get_last_file_name(self) -> None:
        with patch("os.listdir") as listdir, patch("os.path.isfile") as isfile:
            isfile.return_value = True
            listdir.return_value = [
                "filename20221211",
                "filename20211130",
                "filename20230101",
                "filename20201130",
            ]
            expected_value: str = "filename20230101"
            self.assertEqual(
                helpers.get_last_file_name(
                    folder="",
                    filename_template="",
                ),
                expected_value,
            )

    def test_get_src_log_filename(self) -> None:
        with patch("os.path.exists") as exists:
            exists.return_value = False
            with self.assertRaisesRegex(Exception, "неправильный каталог"):
                helpers.get_src_log_filename("", "", logging.Logger(""))
        # Остальной функционал проверяется в test_get_last_file_name


if __name__ == "__main__":
    unittest.main()
