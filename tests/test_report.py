import unittest
import logging

from modules.report import Report
from modules.report_item import ReportItem
from modules.line_attrs import LineAttrs


class TestReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._example_line: str = (
            "1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "
            '"GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" '
            '"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" '
            '"-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390'
        )
        cls._example_line_attrs = LineAttrs(text_line=cls._example_line)
        cls._report_item = ReportItem.from_line_attrs(
            line_attrs=cls._example_line_attrs,
        )
        cls._report = Report("", logging.Logger(""), {"REPORT_DIR": ""})

    def test_0_empty_items(self) -> None:
        self.assertEqual(self._report.total_items, 0)

    def test_1_append_first_item(self) -> None:
        self._report.append(self._example_line_attrs)
        self.assertEqual(self._report.total_items, 1)

    def test_2_calculate(self) -> None:
        # Добавить еще одну строку, такую же, как первая
        self._report.append(self._example_line_attrs)
        # На этом этапе уже есть два элемента в отчете
        another_line: str = self._example_line.replace("25019", "19250")
        self._report.append(LineAttrs(text_line=another_line))
        first_item_key: ReportItem = next(iter(self._report._items.values()))
        self._report.calculate()
        self.assertLess(first_item_key.count_perc - 66.6, 0.07)
        self.assertLess(first_item_key.time_perc - 66.6, 0.07)

    def test_3_total_items(self) -> None:
        self.assertEqual(self._report.total_items, 2)
        # Обогатить уже существующий ReportItem
        self._report.append(self._example_line_attrs)
        self.assertEqual(self._report.total_items, 2)
        # Добавить новый ReportItem
        another_line: str = self._example_line.replace("25019", "29250")
        self._report.append(LineAttrs(text_line=another_line))
        self.assertEqual(self._report.total_items, 3)

    def test_get_date_from_src_filename_raises(self) -> None:
        self._report._src_filename = "filename.txt"
        with self.assertRaisesRegex(Exception, "Ошибка парсинга"):
            self._report._get_date_from_src_filename()

    def test_get_date_from_src_filename(self) -> None:
        self._report._src_filename = "filename20221212.txt"
        self.assertEqual(self._report._get_date_from_src_filename(), "2022.12.12")
        self._report._src_filename = "filename20221213.gz"
        self.assertEqual(self._report._get_date_from_src_filename(), "2022.12.13")
        self._report._src_filename = "filename20241212.tar.gz"
        self.assertEqual(self._report._get_date_from_src_filename(), "2024.12.12")

    def test_get_report_name(self) -> None:
        self._report._reports_dir = "test_dir"
        self._report._src_filename = "log_file.20221031.tar.gz"
        self.assertEqual(
            self._report._get_report_name(), "test_dir/report-2022.10.31.html"
        )


if __name__ == "__main__":
    unittest.main()
